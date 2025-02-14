OpenMetadata provides a default admin account to login.

You can access OpenMetadata at http://localhost:8585. Use the following credentials to log in to OpenMetadata.

Username: admin@open-metadata.org
Password: admin
Once you log in, you can goto Settings -> Users to add another user and make them admin as well.

Log in to Airflow
OpenMetadata ships with an Airflow container to run the ingestion workflows that have been deployed via the UI.

In the Airflow, you will also see some sample DAGs that will ingest sample data and serve as an example.

You can access Airflow at http://localhost:8080. Use the following credentials to log in to Airflow.

Username: admin
Password: admin
Customizing Airflow Admin Credentials:
When using Docker Compose, you can change the default Airflow admin credentials by setting the following environment variables:

Username: AIRFLOW_ADMIN_USER
Password: AIRFLOW_ADMIN_PASSWORD
