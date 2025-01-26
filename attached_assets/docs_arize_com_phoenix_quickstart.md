URL: https://docs.arize.com/phoenix/quickstart
---
☁️ Phoenix Developer Edition🖥️ Run Phoenix Locally

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#create-an-account-and-retrieve-api-key)    Create an account and retrieve API key

1. Create an account on the [**Phoenix website**](https://app.phoenix.arize.com/)

2. Grab your API key from the "Keys" section of the site


![](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252FnGNYFIhKblMIuQcXExUH%252FScreenshot%25202024-10-29%2520at%25202.28.28%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3D55a795b0-26fb-4cdb-8532-80954110eb27&width=768&dpr=4&quality=100&sign=9f9b966d&sv=2)

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#connect-your-app-to-phoenix)    Connect your app to Phoenix

To collect traces from your application, you must configure an OpenTelemetry TracerProvider to send traces to Phoenix. The `register` utility from the `phoenix.otel` module streamlines this process.

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
pip install arize-phoenix
```

Connect your application to your cloud instance using:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import os
from phoenix.otel import register

# Add Phoenix API Key for tracing
PHOENIX_API_KEY = "ADD YOUR API KEY"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

# configure the Phoenix tracer
tracer_provider = register()
```

Your app is now connected to Phoenix! Any OpenTelemetry traces you generate will be sent to your Phoenix instance.

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#instrument-your-app-and-trace-a-request)    Instrument your app and trace a request

Let's generate some of those traces now. We'll use OpenAI in this example, but Phoenix has [dozens of other integrations](https://docs.arize.com/phoenix/tracing/integrations-tracing) to choose from as well.

First we'll import our instrumentor and the OpenAI package:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
pip install openinference-instrumentation-openai openai
```

Then enable our OpenAI integration:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

And finally send a request to OpenAI:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import openai
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku."}],
)
print(response.choices[0].message.content)
```

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#view-traces-in-phoenix)    View traces in Phoenix

You should now see traces in Phoenix!

![](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252FE9QehrKGvt5rFUEKIiEp%252FScreenshot%25202024-10-29%2520at%25202.51.24%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Df00ddb8d-abae-435e-b2bd-5a382adb15f1&width=768&dpr=4&quality=100&sign=afb7d8b5&sv=2)

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#launch-a-local-version-of-phoenix)    Launch a local version of Phoenix

You can use Phoenix's open-source package to launch a local instance of Phoenix on your machine. For more info on other self-hosting options, like Docker, see [Self-hosting](https://docs.arize.com/phoenix/deployment)

First, install the Phoenix package:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
pip install arize-phoenix
```

Then launch your instance in terminal:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
phoenix serve
```

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#connect-your-app-to-phoenix-1)    Connect your app to Phoenix

To collect traces from your application, you must configure an OpenTelemetry TracerProvider to send traces to Phoenix. The `register` utility from the `phoenix` module streamlines this process.

Connect your application to your cloud instance using:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import os
from phoenix.otel import register

# If you have set up auth on your local Phoenix instance, include:
PHOENIX_API_KEY = "ADD YOUR API KEY"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
os.environ["PHOENIX_API_KEY] = "{PHOENIX_API_KEY}"

# configure the Phoenix tracer
tracer_provider = register(
  endpoint="http://localhost:4317",  # Sends traces using gRPC
)
```

Your app is now connected to Phoenix! Any OpenTelemetry traces you generate will be sent to your Phoenix instance.

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#instrument-your-app-and-trace-a-request-1)    Instrument your app and trace a request

Let's generate some of those traces now. We'll use OpenAI in this example, but Phoenix has [dozens of other integrations](https://docs.arize.com/phoenix/tracing/integrations-tracing) to choose from as well.

First we'll import our instrumentor and the OpenAI package:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
pip install openinference-instrumentation-openai openai 'httpx<0.28'
```

Then enable our OpenAI integration:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
from openinference.instrumentation.openai import OpenAIInstrumentor

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

And finally send a request to OpenAI:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import openai
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku."}],
)
print(response.choices[0].message.content)
```

### [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#view-traces-in-phoenix-1)    View traces in Phoenix

You should now see traces in Phoenix!

![](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252FE9QehrKGvt5rFUEKIiEp%252FScreenshot%25202024-10-29%2520at%25202.51.24%25E2%2580%25AFPM.png%3Falt%3Dmedia%26token%3Df00ddb8d-abae-435e-b2bd-5a382adb15f1&width=768&dpr=4&quality=100&sign=afb7d8b5&sv=2)

## [Direct link to heading](https://docs.arize.com/phoenix/quickstart\#next-steps)    Next Steps

- View more details on [tracing](https://docs.arize.com/phoenix/tracing/llm-traces-1)

- Run [evaluations](https://docs.arize.com/phoenix/evaluation/evals) on traces

- Test changes to you prompts, models, and application via [experiments](https://docs.arize.com/phoenix/datasets-and-experiments/how-to-experiments/run-experiments)

- Explore [other hosting options](https://docs.arize.com/phoenix/deployment) for Phoenix


[PreviousArize Phoenix](https://docs.arize.com/phoenix) [NextUser Guide](https://docs.arize.com/phoenix/user-guide)

Last updated 4 days ago

This site uses cookies to deliver its service and to analyse traffic. By browsing this site, you accept the [privacy policy](https://arize.com/privacy-policy/).

AcceptReject

[iframe](https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfESacpAAAAAIAiwrVpFehgscJonmg1gKhpKg2e&co=aHR0cHM6Ly9kb2NzLmFyaXplLmNvbTo0NDM.&hl=en&v=p09oe8YIFfKgcnqQ9m9k4aiB&size=invisible&cb=i4ag2djq0n4a)