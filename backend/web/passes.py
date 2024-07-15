from google.cloud import secretmanager

def google_pass(secret):
  client = secretmanager.SecretManagerServiceClient()
  project_id = ""
  project_version = 'latest'
  secret_id = secret
  name = f"projects/{project_id}/secrets/{secret_id}/versions/{project_version}"
  response = client.access_secret_version(name=name)
  return response.payload.data.decode("UTF-8")