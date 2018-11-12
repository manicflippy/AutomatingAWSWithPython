# -*- coding:utf-8 -*-

"""Classes for Route53 Domains."""

import uuid


class DomainManager:
        """Manage a Route 53 domain."""

        def __init__(self, session):
            """Create DomainManager object."""
            self.session = session
            self.client = self.session.client('route53')

        def find_hosted_zone(self, domain_name):
            """Find and return hosted zone."""
            paginator = self.client.get_paginator('list_hosted_zones')
            for page in paginator.paginate():
                for zone in page['HostedZones']:
                    if domain_name.endswith(zone['Name'][:-1]):
                        return zone

            return None

        def create_hosted_zone(self, domain_name):
            """Create hosted zone."""
            zone_name = '.'.join(domain_name.split('.')[-3:]) + '.'
            return self.client.create_hosted_zone(
                Name=zone_name,
                CallerReference=str(uuid.uuid4())
            )

        def create_s3_domain_record(self, zone, domain_name, endpoint):
            """Create S3 hosted zone for domain name and link to bucket."""
            return self.client.change_resource_record_sets(
                HostedZoneId=zone['Id'],
                ChangeBatch={
                    'Comment': 'Created by webotron',
                    'Changes': [{
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'AliasTarget': {
                                    'HostedZoneId': endpoint.zone,
                                    'DNSName': endpoint.host,
                                    'EvaluateTargetHealth': False
                                },
                            }
                        }
                    ]

                }
            )
