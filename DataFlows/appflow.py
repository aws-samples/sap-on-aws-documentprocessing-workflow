from aws_cdk import(
    aws_appflow as appflow
)

from constructs import Construct

class AppflowConstruct(Construct):
    def __init__(self, scope:Construct, id:str,props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        appflowparams = dict(self.node.try_get_context('appflow'))

        #connector profile 
        self._cfnconnectorprofile = appflow.CfnConnectorProfile(self,
        'sap-connection-profile',
        connection_mode='Public',
        connector_profile_name=appflowparams.get('connection-name'),
        connector_type='SAPOData',
        connector_profile_config=appflow.CfnConnectorProfile.ConnectorProfileConfigProperty(
            connector_profile_credentials=appflow.CfnConnectorProfile.ConnectorProfileCredentialsProperty(
                sapo_data=appflow.CfnConnectorProfile.SAPODataConnectorProfileCredentialsProperty(
                    basic_auth_credentials=appflow.CfnConnectorProfile.BasicAuthCredentialsProperty(
                        username=props["username"],
                        password=props["password"]
                    )
                )
            ),
             connector_profile_properties=appflow.CfnConnectorProfile.ConnectorProfilePropertiesProperty(
                sapo_data=appflow.CfnConnectorProfile.SAPODataConnectorProfilePropertiesProperty(
                application_host_url=appflowparams.get('sap_host'),
                application_service_path=appflowparams.get('sap_catalog_path'),
                port_number=appflowparams.get('sap_port'),
                logon_language=appflowparams.get('sap_langu'),
                client_number=appflowparams.get('sap_client')
            )
            )
        )
        )
     # source flow configuraiton
        _source_connector_flowconfig=appflow.CfnFlow.SourceFlowConfigProperty(
        connector_type="SAPOData",
        source_connector_properties=appflow.CfnFlow.SourceConnectorPropertiesProperty(
            sapo_data=appflow.CfnFlow.SAPODataSourcePropertiesProperty(
                object_path=appflowparams.get('sap_object')
            )
        ),
         connector_profile_name=self._cfnconnectorprofile.connector_profile_name
        )

        _destination_connector_flowconfig=appflow.CfnFlow.DestinationFlowConfigProperty(
            connector_type="S3",
            destination_connector_properties=appflow.CfnFlow.DestinationConnectorPropertiesProperty(
            s3=appflow.CfnFlow.S3DestinationPropertiesProperty(
                bucket_name=props["data_bucket_name"],
            s3_output_format_config=appflow.CfnFlow.S3OutputFormatConfigProperty(
                file_type="JSON"
              )
            )
          )
        )
        
        """
        flowname="".join(["sap-sales-order-s3",'-',props['account']])
      
        #extraction flow
        self.cfn_flow = appflow.CfnFlow(
            self, 'sap-order-extract',
            flow_name=flowname,
            destination_flow_config_list=[_destination_connector_flowconfig],
            source_flow_config=_source_connector_flowconfig,
            tasks=[appflow.CfnFlow.TaskProperty(
                source_fields=[],
                connector_operator=appflow.CfnFlow.ConnectorOperatorProperty(
                sapo_data='NO_OP'),
                task_type="Map_all"
            )],
            trigger_config=appflow.CfnFlow.TriggerConfigProperty(
                trigger_type="Scheduled",
                trigger_properties=appflow.CfnFlow.ScheduledTriggerPropertiesProperty(
                schedule_expression="rate(5minutes)"
                )
            ),
            
        )
        """

        flowname="".join(["s3-sap-order-update",'-',props['account']])
        
        #write back flow
        self.cfn_sap_flow = appflow.CfnFlow(
            self, 'sap-order-update',
            flow_name=flowname,
            source_flow_config=appflow.CfnFlow.SourceFlowConfigProperty(
            connector_type='S3',
            source_connector_properties=appflow.CfnFlow.SourceConnectorPropertiesProperty(
                s3=appflow.CfnFlow.S3SourcePropertiesProperty(
                    bucket_name=props["target_bucket_name"],
                    bucket_prefix=appflowparams.get('prefix'),
                    s3_input_format_config=appflow.CfnFlow.S3InputFormatConfigProperty(
                        s3_input_file_type="JSON"
                    )
                )
            )
            ),
            destination_flow_config_list=[appflow.CfnFlow.DestinationFlowConfigProperty(
                connector_type="SAPOData",
                destination_connector_properties=appflow.CfnFlow.DestinationConnectorPropertiesProperty(
                    sapo_data=appflow.CfnFlow.SAPODataDestinationPropertiesProperty(
                        object_path=appflowparams.get('sap_dest_object'),
                        id_field_names=["SalesOrder","SalesOrderItem"],
                        success_response_handling_config=appflow.CfnFlow.SuccessResponseHandlingConfigProperty(
                            bucket_name=props["target_bucket_name"],
                            bucket_prefix="success"
                        ),
                        write_operation_type="UPDATE"
                    )
                ),
                connector_profile_name=self._cfnconnectorprofile.connector_profile_name
            )],
            tasks=[appflow.CfnFlow.TaskProperty(
                source_fields=["RequestedQuantity"],
                task_type="Map",
                connector_operator=appflow.CfnFlow.ConnectorOperatorProperty(
                    s3="NO_OP"
                ),
                destination_field="RequestedQuantity",
                task_properties=[appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="SOURCE_DATA_TYPE",
                    value="string"
                ),
                appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="DESTINATION_DATA_TYPE",
                    value="Edm.Decimal"
                )]
            ),
            appflow.CfnFlow.TaskProperty(
                source_fields=["SalesOrder"],
                task_type="Map",
                connector_operator=appflow.CfnFlow.ConnectorOperatorProperty(
                    s3="NO_OP"
                ),
                destination_field="SalesOrder",
                task_properties=[appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="SOURCE_DATA_TYPE",
                    value="string"
                ),
                appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="DESTINATION_DATA_TYPE",
                    value="Edm.String"
                )]
            ),
            appflow.CfnFlow.TaskProperty(
                source_fields=["SalesOrderItem"],
                task_type="Map",
                connector_operator=appflow.CfnFlow.ConnectorOperatorProperty(
                    s3="NO_OP"
                ),
                destination_field="SalesOrderItem",
                task_properties=[appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="SOURCE_DATA_TYPE",
                    value="string"
                ),
                appflow.CfnFlow.TaskPropertiesObjectProperty(
                    key="DESTINATION_DATA_TYPE",
                    value="Edm.String"
                )]
            ),

                appflow.CfnFlow.TaskProperty(
                source_fields=["RequestedQuantity","SalesOrder","SalesOrderItem"],
                task_type="Filter",
                connector_operator=appflow.CfnFlow.ConnectorOperatorProperty(
                    s3="PROJECTION"
                )
                  )

            ],
            trigger_config=appflow.CfnFlow.TriggerConfigProperty(
                trigger_type="OnDemand"
            )
        )

        

