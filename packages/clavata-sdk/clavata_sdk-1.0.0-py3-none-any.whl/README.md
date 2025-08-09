# SDK

This is the Clavata SDK for Python.

## Quick Start

For most users, you'll be using the default production API, so unless you've been told otherwise, we recommend using the steps below to create a client.

Set your Clavata API Key in the environment:

```sh
export CLAVATA_API_KEY="YOUR_API_KEY"
```

Then, you can instantiate our client with default settings:

```python
from clavata_sdk import ClavataClient

client = ClavataClient.create()
```

If you wish, you can also inject the API token directly:

```python
from clavata_sdk import ClavataClient

client = ClavataClient.create(auth_token="API_KEY")
```

## Custom host/port

If you've been given a different host and port to connect to, you'll instantiate the client as follows:

```python
from clavata_sdk import ClavataClient
```

Next, you'll need a Clavata API key to instantiate the client:

```python
api_key = "YOUR_API_KEY"

# Now instantiate the client with your API key:
client = ClavataClient(host="gateway.app.clavata.ai", port=443, auth_token=api_key)
```

> As above, the `auth_token` parameter can be omitted if your API key is set in the environment **before** instantiation.

## Basic Use

The client includes methods for evaluation and job retrieval. It also provides access to the request and response types you'll need to pass in.

```python

from clavata_sdk import CreateJobRequest, EvaluateRequest, ContentData

# Async request
response = client.create_job(CreateJobRequest(content=ContentData(...), ...))

# Streaming request
async for response in client.evaluate(EvaluateRequest(content="The quick brown fox", ...)):
    print(response)
```

### Webhooks

The `client.create_job()` method is an async endpoint, which means the job will be started but you'll receive a response before the job has completed. This response is a `Job` and will include the job's ID and status. You can use the job ID to get the results later using the `get_job()` method, but if you'd like to be notified when the job is complete (so you don't have to "poll"), you can add a "webhook". A webhook is a URL that Clavata's platform will make a request to when the job is complete.

To add a webhook to a `create_job()` request, do the following:

```python
from clavata_sdk import ClavataClient, CreateJobRequest

client = ClavataClient.create()
request = CreateJobRequest(content="The quick brown fox", ...).add_webhook(url="https://youdomain.com/path/to/hook")
job = client.create_job(request)

print(job)
```

You can call `add_webhook` on the request object and provide a URL to call. Clavata will make a `POST` request to this URL when the job is complete. You can also optinoally add an `extra_headers` named parameter and provide a dictionary of key/value pairs. Clavata will add these headers to the `POST` request, if provided.

## Dealing with Refusal Errors

Under certain circumstances, the Clavata API may refuse to evaluate a piece of content. Reasons include:

- The content (image) was found in a database of known CSAM material
- The content (image) is in a format that is not currently supported (webp, png, jpg supported as of publishing)
- The content is corrupt, incomplete or otherwise invalid

When the API refuses, an exception will be raised by the SDK. Because exceptions may also be raised for other reasons (i.e., network errors, invalid requests, etc), the SDK provides a distinct error type that both helps you tell when an error is due to a refusal, and also allows you to get more information about why the request was refused.

The `EvaluationRefusedError` type will only be raised if an evaluation was refused for one of the reasons mentioned above.

When a refusal occurs, the response from the API is processed to hydrate this error with information on which pieces of content included in the request were refused, and why each one was refused (if there was more than one piece of content in the request which was refused).

The simplest way to examine refusals is to look at the `refusals` attribute on the error type. It will always be a list containing one entry for each piece of content that was refused. Each entry is of type `RefusedContent` and includes a `reason` as well as the `content_hash` that identifies the piece of content.

```python
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    print("Refused content: ", err.refusals)
```

The error type also comes with a number of additional properties that are useful if you don't want to have to iterate over the entire list of refusals (for example, if you only sent 1 piece of content in the request). These properties are

- `top_reason`: Returns the "most important" reason for the refusal, with CSAM > UNSUPPORTED_FORMAT > INVALID_CONTENT.
- `most_common_reason`: If there are many refusals, returns the most common reason among them. In math terms, the "mode".
- `first_reason`: Always returns the first reason in the list, regardless of how many refusals there were.

You can also access all the content that was refused in a flattened list by using the `refused_content_hashes` property on the error type.

```python
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    print("Refused content: ", err.refusals)

    # Get the first refusal reason
    print("First refusal reason: ", err.first_reason)

    # Get all the content that was refused
    print("Refused hashes: ", err.refused_content_hashes)
```

Finally, the refusal "reasons" are implemented as a python enum, allowing you to easily compare the "reason" in the error to the canonical "reason" values to determine why the content was refused (and then what action to take).

```python
from clavata_sdk import RefusalReason, EvaluationRefusedError
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    if err.first_reason == RefusalReason.CSAM:
        # Now you know that CSAM was found. Act accordingly.
    # etc ...
```

