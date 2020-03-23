from aws_cdk import aws_ecs as _ecs
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import core


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_23'


class LocustFargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: _ec2.IVpc, url: str, tps: int, ** kwargs) -> None:
        """
        Defines an instance of the traffic generator.
        :param scope: construct scope
        :param id:    construct id
        :param vpc:   the VPC in which to host the traffic generator cluster
        :param url:   the URL to hit
        :param tps:   the number of transactions per second
        """
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        locust_cluster = _ecs.Cluster(self,
                                      "locustCluster",
                                      vpc=vpc)

        """
        Load Testing Service in Fargate Cluster
        """

        locust_task_def = _ecs.FargateTaskDefinition(self,
                                                     "locustAppTaskDef"
                                                     )

        locust_container = locust_task_def.add_container("locustAppContainer",
                                                         environment={
                                                             "github_profile": "https://github.com/miztiik",
                                                             "LOCUSTFILE_PATH": "",
                                                             "TARGET_URL": url,
                                                             "LOCUST_OPTS": "--clients=250 --hatch-rate 10 --no-web --run-time=300 --print-stats",
                                                             "ADDTIONAL_CUSTOM_OPTIONS": "--reset-stats --only-summary"
                                                         },
                                                         image=_ecs.ContainerImage.from_registry(
                                                             "locustio/locust:latest"),
                                                         logging=_ecs.LogDrivers.aws_logs(
                                                             stream_prefix="Mystique")
                                                         )

        locust_container.add_port_mappings(
            _ecs.PortMapping(container_port=80, protocol=_ecs.Protocol.TCP)
        )
        locust_container.add_port_mappings(
            _ecs.PortMapping(container_port=443, protocol=_ecs.Protocol.TCP)
        )

        locust_service = _ecs.FargateService(self, 'locustAppService',
                                             cluster=locust_cluster,
                                             task_definition=locust_task_def,
                                             desired_count=2,
                                             assign_public_ip=True,
                                             vpc_subnets=_ec2.SubnetType.PUBLIC,
                                             service_name=f"{global_args.OWNER}-LocustLoadGenerator"
                                             )

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self, "LocustClusterNameOutput",
                                  value=f"{locust_cluster.cluster_name}",
                                  export_name="locustClusterName"
                                  )

        output_2 = core.CfnOutput(self,
                                  "locustAppServiceUrl",
                                  value=f"http://{locust_service.service_name}",
                                  description="To know more about this automation stack, check out our github page."
                                  )