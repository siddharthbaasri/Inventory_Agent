import argparse
import os
import base64
import hashlib
from pathlib import Path
from email.utils import formatdate


# regions:
# us-chicago
# eu-frankfurt-1
# ap-tokyo-1
# ap-osaka-1
# ca-montreal-1
def getEnvVariables():
    region = "us-chicago-1"
    profile = "default_chicago"
    compartment = "ocid1.compartment.oc1..aaaaaaaaxgycba2df5zyupfia7hd36krr36fqtcwyxmfhjbbn2labqnd57za"
    return (region, profile, compartment)

def getEndpoint(region):
    return f"https://inference.generativeai.{region}.oci.oraclecloud.com"
