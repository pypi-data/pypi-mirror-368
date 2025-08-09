import sys
import os

### Uncomment below if you are using a local package ###
# Add the src directory to the Python path to import the local package
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mig_dx_api import DX

# Configuration variables
APP_ID = '{your app id}'
DATASET_NAME = 'My Test Dataset'

# Initialize the client
dx = DX(
  # Your movement app ID
  app_id=APP_ID, 
  # Your private key path (currently looks in the local directory)
  private_key_path=os.path.join(os.path.dirname(__file__), 'privateKey.pem'),
  # You can optionally pass baseUrl if you are using a different URL than the default
  # base_url='https://your-test-url/api/v1/{}'
)

### Uncomment below if you are using a local test server / self-signed certificate ###
# Disable SSL verification for localhost testing
# Override the session_config method to include SSL bypass
# original_session_config = dx.session_config

# def session_config_with_ssl_bypass(self):
#     config = original_session_config()
#     config['verify'] = False  # Disable SSL verification for localhost
#     return config

# Monkey patch the session_config method
# dx.session_config = session_config_with_ssl_bypass.__get__(dx, type(dx))

# # Force reset sessions so they use the new config
# dx._session = None
# dx._asession = None
### End of SSL bypass ###

print("=== Getting All Installations ===")
installations = dx.get_installations()
print(f"Found {len(installations)} installations:")
for installation in installations:
    print(f"  - Installation: {installation.name} (ID: {installation.installation_id})")

# Get the first installation ID
install_id = installations[0].installation_id

print("\n=== Finding Specific Installation ===")
# Find an installation by name or ID
installation = dx.installations.find(install_id=install_id)
print(f"Found installation: {installation.name} (ID: {installation.installation_id})")

print("\n=== Using Installation Context (Method 1) ===")
# Use the installation context
with dx.installation(installation) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    print(f"Found {len(datasets)} datasets in installation '{installation.name}':")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

print("\n=== Using Installation Context (Method 2) ===")
with dx.installation(install_id=install_id) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    print(f"Found {len(datasets)} datasets using install_id={install_id}:")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

print("\n=== Creating New Dataset ===")
# Creating datasets
from mig_dx_api import DatasetSchema, SchemaProperty

# Define the schema
schema = DatasetSchema(
    properties=[
        SchemaProperty(name='my_string', type='string', required=True),
        SchemaProperty(name='my_integer', type='integer', required=True),
        SchemaProperty(name='my_boolean', type='boolean', required=False),
    ],
    primary_key=['my_string']
)
print(f"Created schema with {len(schema.properties)} properties and primary key: {schema.primary_key}")

# Create the dataset
with dx.installation(installation) as ctx:
    print(f"Creating dataset in installation: {installation.name}")
    new_dataset = ctx.datasets.create(
        name=DATASET_NAME,
        description='A test dataset',
        schema=schema.model_dump()  # this can also be defined as a dictionary
    )
    print(f"Successfully created dataset: {new_dataset.name}")

print("\n=== Listing All Datasets After Creation ===")
#  Listing datasets
with dx.installation(installation) as ctx:
    datasets = list(ctx.datasets)
    print(f"Total datasets in installation '{installation.name}': {len(datasets)}")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

# Send some records to the dataset
data = [
    { 'my_string': "my string value", 'my_integer': 10, 'my_boolean': True},
]

with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name=DATASET_NAME)
    dataset_ops.load(data, validate_records=True)  # validate_records=True will validate the records against the schema using Pydantic