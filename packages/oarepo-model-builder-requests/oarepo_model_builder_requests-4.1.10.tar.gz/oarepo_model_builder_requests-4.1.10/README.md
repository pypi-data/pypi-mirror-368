# OARepo model builder requests
Plugin for oarepo-model-builder to allow specifying requests 
tied to the base model, based on invenio requests. <br>

Requests are requests for an action concerning an instance of the model (called 
topic in this context), 
for example to publish the topic. 

The requests are specified as request types (each type has its own class). 
Each request type has pre-specified actions from the invenio framework.
The plugin allows to customize the accept action.


By default, along with changing the request status,
the generated accept action fetches the associated record. It's up to the 
developer to decide what to do with it further.


Requests can be added to the model through "requests" section 
in the yaml file of the model. There can be any number of them.
Options in the yaml:
* `module` Module in which the request is stored. The type and action modules are derived from it but can override the default.
* `type` Settings for the type class of the request. 
Used if the user wants to use a custom request type class.
  * `module`
  * `class`
  * `bases`
  * `imports`
  * `generate` True by defualt, False is 
  typically used when user provides custom Type class.
  * `parent-actions` Request type class specifies actions that can be performed by the request. By default the class imports its parent's possible actions, but this behavior can be customized if the parent class has different structure for some reason.

* `actions`
A list of customized actions by this type of request. Only the accept action is supported for now.
  * `module` 
  * `class` Analogous to type class for the action. By default 
it's [invenio_requests.customizations.AcceptAction](https://github.com/inveniosoftware/invenio-requests/blob/master/invenio_requests/customizations/actions.py).
  * `bases`
  * `imports`
  * `generate` Analogous to type class for the action.

  * `bases` Analogous to type class bases for the action.

It also allows specifying the topic record resolver used. The resolver is tied to the topic class therefore it's generated on record level instead of the request.
Configurable options:
  * `module`
  * `class`
  * `bases`
  * `imports`
  * `generate`
  * `custom-proxy-class` The resolver can use different proxy record resolution class. This is needed for resolving drafts because they don't have registered PIDs.

## Examples

For example, the requests plugin can be used for approving
a thesis. The accept action can be used for approval.
A simple yaml entry at the root level can be used:
```yaml
requests:
  approve-thesis: {}
```
This generates all the basic files. The generated action does
the predefined changes in the default invenio base class, specifically
changes the request status, and provides a template for modifying
the associated thesis record (topic). The template fetches the record and
saves changes on it. What to do with the thesis during is up to the developer.
They have to replace this code with their own implementation.
```python
## todo - do something with the record
# topic["status"] = "accepted"
##
```
Alternatively, they can define the accept action class on their own and import
it instead of generating.
```yaml
requests:
  approve-thesis:
    class: thesis.requests.ApproveAction
    generate: False
```

