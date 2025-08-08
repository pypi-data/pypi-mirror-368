<a id="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AppsApi* | [**add_app**](docs/AppsApi.md#add_app) | **PUT** /apps/ | Add an app to Candela.
*AppsApi* | [**app_exists**](docs/AppsApi.md#app_exists) | **GET** /apps/exists | Check an app exists in Candela.
*AppsApi* | [**delete_app**](docs/AppsApi.md#delete_app) | **DELETE** /apps/ | Delete an app from Candela.
*AppsApi* | [**get_app**](docs/AppsApi.md#get_app) | **GET** /apps/ | Get a specific app definition from Candela.
*AppsApi* | [**get_app_metadata**](docs/AppsApi.md#get_app_metadata) | **GET** /apps/metadata | Get an app's metadata from Candela
*AppsApi* | [**list_apps**](docs/AppsApi.md#list_apps) | **GET** /apps/list | List all the apps available to you in Candela.
*CircuitsApi* | [**add_circuit**](docs/CircuitsApi.md#add_circuit) | **PUT** /circuits/ | Add a circuit to Candela.
*CircuitsApi* | [**circuit_exists**](docs/CircuitsApi.md#circuit_exists) | **GET** /circuits/exists | Check that a given circuit exists in Candela.
*CircuitsApi* | [**delete_circuit**](docs/CircuitsApi.md#delete_circuit) | **DELETE** /circuits/ | Delete a given circuit from Candela.
*CircuitsApi* | [**get_circuit**](docs/CircuitsApi.md#get_circuit) | **GET** /circuits/ | Get a given circuit from Candela.
*CircuitsApi* | [**get_circuit_metadata**](docs/CircuitsApi.md#get_circuit_metadata) | **GET** /circuits/metadata | Get a given circuit's metadata from Candela
*CircuitsApi* | [**list_circuits**](docs/CircuitsApi.md#list_circuits) | **GET** /circuits/list | List all the circuits available to you in Candela.
*DirectivesApi* | [**add_directive**](docs/DirectivesApi.md#add_directive) | **PUT** /directives/ | Add a directive to Candela.
*DirectivesApi* | [**delete_directive**](docs/DirectivesApi.md#delete_directive) | **DELETE** /directives/ | Delete a directive from Candela.
*DirectivesApi* | [**directive_exists**](docs/DirectivesApi.md#directive_exists) | **GET** /directives/exists | Check if a particular directive exists in Candela.
*DirectivesApi* | [**get_directive**](docs/DirectivesApi.md#get_directive) | **GET** /directives/ | Get a directive from Candela.
*DirectivesApi* | [**get_directive_metadata**](docs/DirectivesApi.md#get_directive_metadata) | **GET** /directives/metadata | Get a directive's metadata from Candela.
*DirectivesApi* | [**list_directives**](docs/DirectivesApi.md#list_directives) | **GET** /directives/list | List your available directives in Candela.
*ModelsApi* | [**add_model**](docs/ModelsApi.md#add_model) | **PUT** /models/ | Add an LLM model to Candela.
*ModelsApi* | [**delete_model**](docs/ModelsApi.md#delete_model) | **DELETE** /models/ | Delete a model in Candela.
*ModelsApi* | [**get_model_metadata**](docs/ModelsApi.md#get_model_metadata) | **GET** /models/metadata | Get metadata for a model in Candela.
*ModelsApi* | [**list_models**](docs/ModelsApi.md#list_models) | **GET** /models/list | List all models available to you in Candela.
*ModelsApi* | [**model_exists**](docs/ModelsApi.md#model_exists) | **GET** /models/exists | Check that a model exists in Candela.
*SessionsApi* | [**delete_session**](docs/SessionsApi.md#delete_session) | **DELETE** /sessions/ | Delete all data associated with a session in Candela.
*SessionsApi* | [**get_session**](docs/SessionsApi.md#get_session) | **GET** /sessions/ | Get the details of a session in Candela.
*SessionsApi* | [**get_session_metadata**](docs/SessionsApi.md#get_session_metadata) | **GET** /sessions/metadata | Get the metadata associated with a session in Candela.
*SessionsApi* | [**list_sessions**](docs/SessionsApi.md#list_sessions) | **GET** /sessions/list | Start an agent/pipeline session on your assigned slot in Candela.
*SessionsApi* | [**session_exists**](docs/SessionsApi.md#session_exists) | **GET** /sessions/exists | Check whether a session with a given ID exists.
*SessionsApi* | [**start_dev_session**](docs/SessionsApi.md#start_dev_session) | **POST** /session/dev | Start an agent/pipeline session on your slot.
*SessionsApi* | [**start_session**](docs/SessionsApi.md#start_session) | **POST** /session | Start an agent/pipeline session on your slot.
*SessionsApi* | [**stop_session**](docs/SessionsApi.md#stop_session) | **GET** /session/stop | Stop an agent/pipeline session.
*SessionsApi* | [**submit_pipeline_prompt**](docs/SessionsApi.md#submit_pipeline_prompt) | **POST** /session/pipeline_submit | Send a prompt to a running pipeline session.
*SessionsApi* | [**submit_prompt_to_agent**](docs/SessionsApi.md#submit_prompt_to_agent) | **POST** /session/agent_submit | Send a prompt to a running agent session.
*SystemApi* | [**admin_delete_slot**](docs/SystemApi.md#admin_delete_slot) | **DELETE** /system/slot | Deletes a slot from the system without replacing it
*SystemApi* | [**get_domain_state**](docs/SystemApi.md#get_domain_state) | **GET** /system/status | Get the current status of your Candela platform slots infrastructure.
*SystemApi* | [**list_slots**](docs/SystemApi.md#list_slots) | **GET** /system/list_slots | List the current slots in your Candela platform.
*SystemApi* | [**set_free_slots_target**](docs/SystemApi.md#set_free_slots_target) | **PUT** /system/free_slots_target | Set the target number of free slots
*SystemApi* | [**set_max_slots**](docs/SystemApi.md#set_max_slots) | **PUT** /system/max_slots | Set the maximum number of slots.
*ToolModulesApi* | [**add_tool_module**](docs/ToolModulesApi.md#add_tool_module) | **PUT** /tool_modules/ | Add a tool module to Candela.
*ToolModulesApi* | [**delete_tool_module**](docs/ToolModulesApi.md#delete_tool_module) | **DELETE** /tool_modules/ | Delete a tool module from Candela.
*ToolModulesApi* | [**get_tool_metadata**](docs/ToolModulesApi.md#get_tool_metadata) | **GET** /tool_modules/tool/metadata | Get the metadata associated with a specific tool in Candela.
*ToolModulesApi* | [**get_tool_module**](docs/ToolModulesApi.md#get_tool_module) | **GET** /tool_modules/ | Get the content of a given tool module from Candela.
*ToolModulesApi* | [**get_tool_module_metadata**](docs/ToolModulesApi.md#get_tool_module_metadata) | **GET** /tool_modules/metadata | Get the metadata associated with a tool module in Candela.
*ToolModulesApi* | [**list_tool_modules**](docs/ToolModulesApi.md#list_tool_modules) | **GET** /tool_modules/list | List all tool modules available in Candela.
*ToolModulesApi* | [**list_tools**](docs/ToolModulesApi.md#list_tools) | **GET** /tool_modules/tool/list | List all tools contained in all modules in Candela.
*ToolModulesApi* | [**tool_exists**](docs/ToolModulesApi.md#tool_exists) | **GET** /tool_modules/tool/exists | Check whether a tool with a given name exists in a scope in Candela.
*ToolModulesApi* | [**tool_module_exists**](docs/ToolModulesApi.md#tool_module_exists) | **GET** /tool_modules/exists | Check whether a given tool module exists in Candela.
*TracesApi* | [**get_trace**](docs/TracesApi.md#get_trace) | **GET** /traces/ | Get the contents of a trace from Candela.
*TracesApi* | [**list_traces**](docs/TracesApi.md#list_traces) | **GET** /traces/list | List all traces available in Candela.
*UserSlotsApi* | [**assign_slot**](docs/UserSlotsApi.md#assign_slot) | **PUT** /slot | Assign a slot to yourself.
*UserSlotsApi* | [**dispose_slot**](docs/UserSlotsApi.md#dispose_slot) | **DELETE** /slot | Dispose of your slot.
*UserSlotsApi* | [**get_slot_metadata**](docs/UserSlotsApi.md#get_slot_metadata) | **GET** /slot/metadata | Get the metadata of your slot.
*UserSlotsApi* | [**get_slot_state**](docs/UserSlotsApi.md#get_slot_state) | **GET** /slot/state | Get the state of your slot.
*UserSlotsApi* | [**user_has_slot**](docs/UserSlotsApi.md#user_has_slot) | **GET** /slot/user_has_slot | Check if you have a slot assigned to you.


<a id="documentation-for-models"></a>
## Documentation for Models

 - [AppSpec](docs/AppSpec.md)
 - [BaseTool](docs/BaseTool.md)
 - [CircuitDTO](docs/CircuitDTO.md)
 - [ConfirmDTO](docs/ConfirmDTO.md)
 - [DTOArr](docs/DTOArr.md)
 - [DTOBool](docs/DTOBool.md)
 - [DTOConst](docs/DTOConst.md)
 - [DTODict](docs/DTODict.md)
 - [DTOEnum](docs/DTOEnum.md)
 - [DTOInt](docs/DTOInt.md)
 - [DTOObj](docs/DTOObj.md)
 - [DTOReal](docs/DTOReal.md)
 - [DTOStr](docs/DTOStr.md)
 - [DevSessionStartRequest](docs/DevSessionStartRequest.md)
 - [Directive](docs/Directive.md)
 - [Event](docs/Event.md)
 - [Fields](docs/Fields.md)
 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [InsertContextDTO](docs/InsertContextDTO.md)
 - [IntentDTO](docs/IntentDTO.md)
 - [Keys](docs/Keys.md)
 - [NoOpDTO](docs/NoOpDTO.md)
 - [Nodes](docs/Nodes.md)
 - [Obj](docs/Obj.md)
 - [Obj1](docs/Obj1.md)
 - [ObjectId](docs/ObjectId.md)
 - [ObjectMetadata](docs/ObjectMetadata.md)
 - [PostApp](docs/PostApp.md)
 - [PostCircuit](docs/PostCircuit.md)
 - [PostDirective](docs/PostDirective.md)
 - [PostToolModule](docs/PostToolModule.md)
 - [ResponseDTO](docs/ResponseDTO.md)
 - [Session](docs/Session.md)
 - [SessionStartRequest](docs/SessionStartRequest.md)
 - [SlotData](docs/SlotData.md)
 - [SlotState](docs/SlotState.md)
 - [SlotsPutResponse](docs/SlotsPutResponse.md)
 - [Spec](docs/Spec.md)
 - [SubmitPrompt](docs/SubmitPrompt.md)
 - [SwitchDTO](docs/SwitchDTO.md)
 - [ToolMetadata](docs/ToolMetadata.md)
 - [ToolModule](docs/ToolModule.md)
 - [ToolModuleMetadata](docs/ToolModuleMetadata.md)
 - [ToolObj](docs/ToolObj.md)
 - [Trace](docs/Trace.md)
 - [TraceItem](docs/TraceItem.md)
 - [UseToolDTO](docs/UseToolDTO.md)
 - [ValidationError](docs/ValidationError.md)
 - [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)

