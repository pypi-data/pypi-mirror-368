import xlsxwriter
from gitlab_evaluate.lib import utils
from gitlab_evaluate.migration_readiness.jenkins.evaluate import JenkinsEvaluateClient
from gitlab_evaluate.migration_readiness.jenkins.data_classes.plugin import JenkinsPlugin

class ReportGenerator():
    def __init__(self, host, user, token, filename=None, output_to_screen=False, evaluate_api=None, processes=None, ssl_verify=True):
        self.host = host
        self.jenkins_client = JenkinsEvaluateClient(host, user, token, ssl_verify, processes=processes)
        if filename:
            self.workbook = xlsxwriter.Workbook(f'{filename}.xlsx')
        else:
            self.workbook = xlsxwriter.Workbook('evaluate_report.xlsx')
        self.app_stats = self.workbook.add_worksheet('App Stats')
        self.align_left = self.workbook.add_format({'align': 'left'})
        # Create Header format with a black background
        self.header_format = self.workbook.add_format({'bg_color': 'black', 'font_color': 'white', 'bold': True, 'font_size': 10})
        self.workbook.add_format({'text_wrap': True, 'font_size': 10})
        self.plugins = self.workbook.add_worksheet('Plugins')
        self.raw_output = self.workbook.add_worksheet('Raw Job Data')
        self.output_to_screen = output_to_screen
        self.processes = processes
        self.columns = [
            'fullname',
            'name',
            'url',
            'color',
            '_class',
            'execution_frequency',
            'avg_duration',
            'success_rate',
            'cpu_usage',
            'memory_usage',
            'cluster_label',
            'predicted_impact',
            'anomaly'
        ]
        self.plugin_columns = list(JenkinsPlugin.__annotations__.keys())

        utils.write_headers(0, self.raw_output, self.columns, self.header_format)
        utils.write_headers(0, self.plugins, self.plugin_columns, self.header_format)

    def write_workbook(self):
        self.app_stats.autofit()
        self.raw_output.autofit()
        self.plugins.autofit()
        self.workbook.close()

    def get_app_stats(self):
        '''
            Gets Jenkins instance stats
        '''
        report_stats = []
        report_stats += [
            ('Basic information from source', self.host),
            ('Customer', '<CUSTOMERNAME>'),
            ('Date Run', utils.get_date_run()),
            ('Source', 'Jenkins'),
            ('Jenkins Version', self.jenkins_client.server.get_version()),
            ('Total Jobs', self.jenkins_client.server.jobs_count()),
            ('Total Plugins Installed', len(self.jenkins_client.plugins))
        ]
        for row, stat in enumerate(report_stats):
            self.app_stats.write(row, 0, stat[0])
            self.app_stats.write(row, 1, stat[1])
        return report_stats

    def get_app_stat_extras(self, report_stats):
        '''
            Writes a series of rows with formulas to other sheets to get additional counts
        '''
        additional_stats = [
            ('Total Plugins Needing an Update', f"={utils.get_countif(self.plugins.get_name(), 'True', 'E')}"),
            ('Total Plugins Enabled', f"={utils.get_countif(self.plugins.get_name(), 'True', 'F')}")
        ]
        for job_type in self.jenkins_client.job_types:
            additional_stats.append(
                (f"Total '{job_type}' jobs", f"={utils.get_countif(self.raw_output.get_name(), job_type, 'E')}")
            )
        starting_point = len(report_stats)
        for row, stat in enumerate(additional_stats):
            self.app_stats.write(row+starting_point, 0, stat[0])
            self.app_stats.write(row+starting_point, 1, stat[1])

    def get_plugins(self):
        """
            Gets a list of plugins and writes the data to the 'Plugins' sheet
        """
        count = 0
        for row, plugin in enumerate(self.jenkins_client.list_of_plugins()):
            for col, col_name in enumerate(self.plugin_columns):
                self.plugins.write(row+1, col, getattr(plugin, col_name))
            count += 1
        print(f"Retrieved {count} plugins")

    def get_raw_data(self):
        '''
            Retrieves a list of Jenkins Jobs and writes all the data to the 'Raw Job Data' sheet
        '''
        job_data = self.jenkins_client.build_full_job_list()
        print(f"Retrieved {self.jenkins_client.server.num_jobs} jobs")

        # Train models
        predictive_model, predictive_scaler = self.jenkins_client.train_predictive_model(job_data)
        anomaly_model, anomaly_scaler = self.jenkins_client.train_anomaly_detection_model(job_data)

        # Perform clustering if there are enough jobs
        job_labels = self.jenkins_client.cluster_jobs(job_data) if len(job_data) >= 3 else [0] * len(job_data)

        # Detect anomalies
        anomalies = self.jenkins_client.detect_anomalies(anomaly_model, anomaly_scaler, job_data)

        for row, (job, label, anomaly) in enumerate(zip(job_data, job_labels, anomalies)):
            predicted_impact = self.jenkins_client.predict_impact(predictive_model, predictive_scaler, job)
            job['cluster_label'] = label
            job['predicted_impact'] = predicted_impact
            job['anomaly'] = anomaly

            # Write job data and analysis results to the raw output sheet
            for col, col_name in enumerate(self.columns):
                self.raw_output.write(row + 1, col, job.get(col_name, "N/A"))

