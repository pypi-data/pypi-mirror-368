from lattica_query.lattica_query_client import QueryClient
from lattica_common.dev_utils.dev_mod_utils import RunMode, RUN_MODE, mock_upload_pk


class LocalQueryClient(QueryClient):

    def upload_evaluation_key_file(self, pk_filename: str) -> None:
        """
        Upload the user's evaluation key file to the Lattica server,
        alert the server that upload completed, and then have the worker
        preprocess the key.
        """
        print(f"Uploading evaluation key file '{pk_filename}' to server...")
        s3_key = self.agent_app.upload_user_file(pk_filename)
        if RUN_MODE is RunMode.RUN_LOCAL_WITH_API:
            mock_upload_pk(pk_filename, s3_key)

        alert_upload_complete = self.agent_app.alert_upload_complete(s3_key)
        print(f"pk {pk_filename} uploaded status is {alert_upload_complete}.")

        print(f"Calling to preprocess {pk_filename}")
        self.worker_api.preprocess_pk()
        print("Evaluation key preprocessing on worker is complete.")

        return
