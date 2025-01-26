URL: https://docs.arize.com/phoenix
---
Phoenix is an open-source observability library designed for experimentation, evaluation, and troubleshooting. It allows AI Engineers and Data Scientists to quickly visualize their data, evaluate performance, track down issues, and export data to improve.

Phoenix is built by [Arize AI](https://www.arize.com/), the company behind the industry-leading AI observability platform, and a set of core contributors.

## [Direct link to heading](https://docs.arize.com/phoenix\#install-phoenix)    Install Phoenix

Using pipUsing condaContainer

In your Jupyter or Colab environment, run the following command to install.

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
pip install arize-phoenix
```

For full details on how to run phoenix in various environments such as Databricks, consult our [environments guide.](https://docs.arize.com/phoenix/deployment/environments)

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
conda install -c conda-forge arize-phoenix[evals]
```

Phoenix can also run via a container. The image can be found at:

[![Logo](https://hub.docker.com/favicon.ico)Docker](https://hub.docker.com/r/arizephoenix/phoenix)

Images for phoenix are published to dockerhub

Checkout the [environments section](https://docs.arize.com/phoenix/deployment/environments) and [deployment guide](https://docs.arize.com/phoenix/deployment/deploying-phoenix) for details.

Phoenix works with OpenTelemetry and [OpenInference](https://github.com/Arize-ai/openinference) instrumentation. If you are looking to deploy phoenix as a service rather than a library, see [Self-hosting](https://docs.arize.com/phoenix/deployment)

## [Direct link to heading](https://docs.arize.com/phoenix\#quickstarts)    Quickstarts

Running Phoenix for the first time? Select a quickstart below.

[![Cover](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252Fgit-blob-d6b9a974cfd0d3bb072dda98055c8a1048a638e2%252FScreenshot%25202023-09-27%2520at%25201.51.45%2520PM.png%3Falt%3Dmedia&width=376&dpr=4&quality=100&sign=61005cf0&sv=2)\\
\\
**Tracing**](https://docs.arize.com/phoenix/tracing/llm-traces-1) [![Cover](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252Fgit-blob-2f1ce146666b874e3bf4d103e43f58a672fb9d5b%252Fevals.png%3Falt%3Dmedia&width=376&dpr=4&quality=100&sign=e0169fd5&sv=2)\\
\\
**Evaluation**](https://docs.arize.com/phoenix/evaluation/evals) [![Cover](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252Fgit-blob-dc8c8be7d64ab910d0d1815a0390c0b8c2aa2aa0%252FScreenshot%25202023-09-27%2520at%25201.53.06%2520PM.png%3Falt%3Dmedia&width=376&dpr=4&quality=100&sign=c4b27343&sv=2)\\
\\
**Inferences**](https://docs.arize.com/phoenix/inferences/phoenix-inferences) [![Cover](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252Fgit-blob-ed9556c4c42b5614588d719a1c6ebce3382e0594%252Fexperiments_preview.png%3Falt%3Dmedia&width=376&dpr=4&quality=100&sign=b6fa8c0c&sv=2)\\
\\
**Datasets and Experiments**](https://docs.arize.com/phoenix/datasets-and-experiments/quickstart-datasets)

## [Direct link to heading](https://docs.arize.com/phoenix\#available-packages)    Available Packages

The main Phoenix package is arize-phoenix. We offer several helper packages below for specific use cases.

Package

What It's For

Pypi

arize-phoenix

Running and connecting to the Phoenix client. Used:
\- Self-hosting Phoenix
\- Connecting to a Phoenix client (either Phoenix Developer Edition or self-hosted) to query spans, run evaluations, generate datasets, etc.

_\*arize-phoenix automatically includes arize-phoenix-otel and arize-phoenix evals_

![PyPI - Version](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Farize-phoenix&width=300&dpr=4&quality=100&sign=19d24992&sv=2)

arize-phoenix-otel

Sending OpenTelemetry traces to a Phoenix instance

![PyPI - Version](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Farize-phoenix-otel&width=300&dpr=4&quality=100&sign=d416bc79&sv=2)

arize-phoenix-evals

Running evaluations in your environment

![PyPI - Version](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Farize-phoenix-evals&width=300&dpr=4&quality=100&sign=662b2f8c&sv=2)

openinference-semantic-conventions

Our semantic layer to add LLM telemetry to OpenTelemetry

![PyPI - Version](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2Fimg.shields.io%2Fpypi%2Fv%2Fopeninference-semantic-conventions&width=300&dpr=4&quality=100&sign=61540c70&sv=2)

openinference-instrumentation-xxxx

Automatically instrumenting popular packages.

See [Integrations: Tracing](https://docs.arize.com/phoenix/tracing/integrations-tracing)

## [Direct link to heading](https://docs.arize.com/phoenix\#next-steps)    Next Steps

### [Direct link to heading](https://docs.arize.com/phoenix\#try-our-tutorials)    [Try our Tutorials](https://docs.arize.com/phoenix/notebooks)

Check out a comprehensive list of example notebooks for LLM Traces, Evals, RAG Analysis, and more.

### [Direct link to heading](https://docs.arize.com/phoenix\#community)    [Community](https://join.slack.com/t/arize-ai/shared_invite/zt-1ppbtg5dd-1CYmQO4dWF4zvXFiONTjMg)

Join the Phoenix Slack community to ask questions, share findings, provide feedback, and connect with other developers.

[NextQuickstart](https://docs.arize.com/phoenix/quickstart)

Last updated 4 days ago

This site uses cookies to deliver its service and to analyse traffic. By browsing this site, you accept the [privacy policy](https://arize.com/privacy-policy/).

AcceptReject

[iframe](https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfESacpAAAAAIAiwrVpFehgscJonmg1gKhpKg2e&co=aHR0cHM6Ly9kb2NzLmFyaXplLmNvbTo0NDM.&hl=en&v=p09oe8YIFfKgcnqQ9m9k4aiB&size=invisible&cb=m045lv407sz2)