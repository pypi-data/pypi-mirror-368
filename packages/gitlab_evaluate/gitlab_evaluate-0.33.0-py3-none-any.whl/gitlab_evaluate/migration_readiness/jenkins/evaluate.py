import os, re
from dacite import from_dict
from gitlab_evaluate.migration_readiness.jenkins.data_classes.plugin import JenkinsPlugin
from sklearn.cluster import KMeans
import numpy as np
import torch.nn as nn
import torch
import sqlite3
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from gitlab_ps_utils.processes import MultiProcessing
from gitlab_evaluate.migration_readiness.jenkins.jenkins import MultiProcessJenkins
from gitlab_evaluate.migration_readiness.jenkins.auto_encoder import AutoEncoder
from gitlab_evaluate.migration_readiness.jenkins.simple_neural_network import SimpleNN

class JenkinsEvaluateClient():
    def __init__(self, host, user, token, ssl_verify, processes=None) -> None:
        self.setup_db()
        self.processes = processes
        self.server = MultiProcessJenkins(host, username=user, password=token, ssl_verify=ssl_verify, processes=self.processes)
        self.user = self.server.get_whoami()
        self.version = self.server.get_version()
        self.plugins = self.server.get_plugins_info()
        self.jobs, self.job_types = self.server.get_all_jobs()
        self.multi = MultiProcessing()

    def setup_db(self):
        if os.path.exists('jenkins.db'):
            os.remove('jenkins.db')
        con = sqlite3.connect('jenkins.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("CREATE TABLE jobs(_class, name, url, color, fullName UNIQUE)")
        cur.execute("CREATE TABLE job_types(type)")
        cur.execute("CREATE TABLE jobs_to_process(id UNIQUE, job)")
        con.commit()
        con.close()
    
    def drop_tables(self):
        con = sqlite3.connect('jenkins.db')
        cur = con.cursor()
        cur.execute("DROP TABLE jobs")
        cur.execute("DROP TABLE job_types")
        con.commit()
        con.close()

    def list_of_plugins(self):
        for plugin in self.plugins:
            yield from_dict(JenkinsPlugin, plugin)
    
    def estimate_resource_usage(self, job_name):
        """
        Estimates CPU and memory usage based on build duration and job type.
        """
        builds = self.server.get_job_info(job_name).get('builds', [])
        total_cpu_usage = 0
        total_memory_usage = 0
        build_count = 0

        for build in builds:
            build_number = build.get('number')
            build_info = self.server.get_build_info(job_name, build_number)
            duration = build_info.get('duration', 0)  # in milliseconds
            # Estimate CPU usage as a function of duration
            estimated_cpu = self.estimate_cpu_usage(duration)
            # Estimate memory usage based on job type or other factors
            estimated_memory = self.estimate_memory_usage(job_name)
            total_cpu_usage += estimated_cpu
            total_memory_usage += estimated_memory
            build_count += 1

        avg_cpu = total_cpu_usage / build_count if build_count > 0 else 0
        avg_memory = total_memory_usage / build_count if build_count > 0 else 0

        return {
            'cpu': avg_cpu,
            'memory': avg_memory
        }

    def estimate_cpu_usage(self, duration):
        """
        Estimates CPU usage based on build duration.
        """
        # Convert duration from milliseconds to seconds
        duration_seconds = duration / 1000.0
        # We assume CPU usage is proportional to duration
        # Arbitrary factor - Here we asssume that 1 seconds represents 1/2 cpu usage
        cpu_usage = duration_seconds * 0.5 
        return cpu_usage

    def estimate_memory_usage(self, job_name):
        """
        Estimates memory usage based on job type or characteristics.
        """
        job_info = self.server.get_job_info(job_name)
        job_class = job_info.get('_class', '')
        if 'Maven' in job_class:
            return 1024  # Assume Maven jobs use 1024MB on average
        elif 'WorkflowJob' in job_class:
            return 2048  # Assume Pipeline jobs use 2048MB on average
        else:
            return 512  # Default memory usage in MB for other job types

    def build_job_data(self, job):
        job_name = job['fullName']
        job_history = self.get_job_history(job_name)
        total_executions = len(job_history)
        total_duration = sum(build['duration'] for build in job_history)
        success_count = sum(1 for build in job_history if build['result'] == 'SUCCESS')
        avg_duration = total_duration / total_executions if total_executions > 0 else 0
        success_rate = success_count / total_executions if total_executions > 0 else 0

        resource_usage = self.estimate_resource_usage(job_name)

        return {
            'fullname': job.get('fullName', "N/A"),
            'name': job_name,
            'url': job.get('url', "N/A"),
            'color': job.get('color', "N/A"),
            '_class': job.get('_class', "N/A"),
            'execution_frequency': total_executions,
            'avg_duration': avg_duration,
            'success_rate': success_rate,
            'cpu_usage (estimate)': resource_usage['cpu'],
            'memory_usage (estimate)': resource_usage['memory']
        }
    
    def build_full_job_list(self):
        return list(self.multi.start_multi_process(self.build_job_data, self.jobs, processes=self.processes))

    def get_job_history(self, job_name):
        # Retrieve job build history and return relevant data
        builds = self.server.get_job_info(job_name).get('builds', [])
        build_data = []
        for build in builds:
            build_info = self.server.get_build_info(job_name, build.get('number'))
            build_data.append({
                'number': build.get('number', 'N/A'),
                'duration': build_info.get('duration', 0),
                'result': build_info.get('result', 'UNKNOWN'),
                'timestamp': build_info.get('timestamp', 0)
            })
        return build_data
    
    def train_predictive_model(self, job_data):
        input_size = 2
        hidden_size = 10
        output_size = 1
        model = SimpleNN(input_size, hidden_size, output_size)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        X = np.array([[job['execution_frequency'], job['avg_duration']] for job in job_data])
        y = np.array([job['success_rate'] for job in job_data])
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        y = y.reshape(-1, 1)

        dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32))
        dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

        model.train()
        for epoch in range(100):  # loop over the dataset multiple times
            for inputs, targets in dataloader:
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        return model, scaler

    def predict_impact(self, model, scaler, job):
        model.eval()
        inputs = scaler.transform([[job['execution_frequency'], job['avg_duration']]])
        inputs = torch.tensor(inputs, dtype=torch.float32)
        output = model(inputs).item()
        return output

    def train_anomaly_detection_model(self, job_data):
        input_size = 3
        hidden_size = 2
        model = AutoEncoder(input_size, hidden_size)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        X = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        dataset = TensorDataset(torch.tensor(X, dtype=torch.float32))
        dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

        model.train()
        for epoch in range(100):  # loop over the dataset multiple times
            for inputs, in dataloader:
                outputs = model(inputs)
                loss = criterion(outputs, inputs)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        return model, scaler

    def detect_anomalies(self, model, scaler, job_data):
        model.eval()
        X = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        X = scaler.transform(X)
        inputs = torch.tensor(X, dtype=torch.float32)
        outputs = model(inputs)
        losses = ((outputs - inputs) ** 2).mean(dim=1).detach().numpy()

        return losses > np.percentile(losses, 95)
    
    def cluster_jobs(self, job_data):
        # Convert job data to a suitable format for clustering
        job_features = np.array([[job['execution_frequency'], job['avg_duration'], job['success_rate']] for job in job_data])
        kmeans = KMeans(n_clusters=min(3, len(job_data)), random_state=0).fit(job_features)
        return kmeans.labels_
