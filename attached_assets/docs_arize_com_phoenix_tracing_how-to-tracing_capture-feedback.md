URL: https://docs.arize.com/phoenix/tracing/how-to-tracing/capture-feedback
---
feedback and annotations are available for arize-phoenix>=4.20.0

![](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2F3394180728-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FShR775Rt7OzHRfy5j2Ks%252Fuploads%252Fgit-blob-c57f29f4c0a645d16957e5ff3c7dc60c50c0e574%252Ffeedback_flow.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=4b03848f&sv=2)

When building LLM applications, it is important to collect feedback to understand how your app is performing in production. The ability to observe user feedback along with traces can be very powerful as it allows you to drill down into the most interesting examples. Once you have identified these example, you can share them for further review, automatic evaluation, or fine-tuning.

Phoenix lets you attach user feedback to spans and traces in the form of annotations. It's helpful to expose a simple mechanism (such as 👍👎) to collect user feedback in your app. You can then use the Phoenix API to attach feedback to a span.

Phoenix expects feedback to be in the form of an **annotation.** Annotations consist of these fields:

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
{
  "span_id": "67f6740bbe1ddc3f", // the id of the span to annotate
  "name": "correctness", // the name of your annotator
  "annotator_kind": "HUMAN", // HUMAN or LLM
  "result": {
    "label": "correct", // A human-readable category for the feedback
    "score": 1, // a numeric score, can be 0 or 1, or a range like 0 to 100
    "explanation": "The response answered the question I asked"
   }
}
```

Note that you can provide a **label**, a **score**, or both. With Phoenix an annotation has a name (like **correctness**), is associated with an **annotator** (either an **LLM** or a **HUMAN**) and can be attached to the **spans** you have logged to Phoenix.

## [Direct link to heading](https://docs.arize.com/phoenix/tracing/how-to-tracing/capture-feedback\#send-annotations-to-phoenix)    Send Annotations to Phoenix

Once you construct the annotation, you can send this to Phoenix via it's REST API. You can POST an annotation from your application to `/v1/span_annotations` like so:

If you're self-hosting Phoenix, be sure to change the endpoint in the code below to `<your phoenix endpoint>/v1/span_annotations?sync=false`

PythonTypeScriptcurl

**Retrieve the current span\_id**

If you'd like to collect feedback on currently instrumented code, you can get the current span using the `opentelemetry` SDK.

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
from opentelemetry import trace

span = trace.get_current_span()
span_id = span.get_span_context().span_id.to_bytes(8, "big").hex()
```

You can use the span\_id to send an annotation associated with that span.

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import httpx

client = httpx.Client()

annotation_payload = {
    "data": [\
        {\
            "span_id": span_id,\
            "name": "user feedback",\
            "annotator_kind": "HUMAN",\
            "result": {"label": "thumbs-up", "score": 1},\
            "metadata": {},\
        }\
    ]
}

headers = {'api_key': '<your phoenix api key>'}

client.post(
    "https://app.phoenix.arize.com/v1/span_annotations?sync=false",
    json=annotation_payload,
    headers=headers
)
```

**Retrieve the current spanId**

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
import { trace } from "@opentelemetry/api";

async function chat(req, res) {
  // ...
  const spanId = trace.getActiveSpan()?.spanContext().spanId;
}
```

You can use the spanId to send an annotation associated with that span.

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
async function postFeedback(spanId: string) {
  // ...
  await fetch("https://app.phoenix.arize.com/v1/span_annotations?sync=false", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      accept: "application/json",
      "api_key": "<your phoenix api key>,
    },
    body: JSON.stringify({
      data: [\
        {\
          span_id: spanId,\
          annotator_kind: "HUMAN",\
          name: "feedback",\
          result: {\
            label: "thumbs_up",\
            score: 1,\
            explanation: "A good response",\
          },\
        },\
      ],
    }),
  });
}
```

Copy

```min-w-full inline-grid [grid-template-columns:auto_1fr] py-2 px-2 [counter-reset:line]
curl -X 'POST' \
  'https://app.phoenix.arize.com/v1/span_annotations?sync=false' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'api_key: <your phoenix api key> \
  -d '{
  "data": [\
    {\
      "span_id": "67f6740bbe1ddc3f",\
      "name": "correctness",\
      "annotator_kind": "HUMAN",\
      "result": {\
        "label": "correct",\
        "score": 1,\
        "explanation": "it is correct"\
      },\
      "metadata": {}\
    }\
  ]
}'
```

## [Direct link to heading](https://docs.arize.com/phoenix/tracing/how-to-tracing/capture-feedback\#annotate-traces-in-the-ui)    Annotate Traces in the UI

Phoenix also allows you to manually annotate traces with feedback within the application. This can be useful for adding context to a trace, such as a user's comment or a note about a specific issue. You can annotate a span directly from the span details view.

![](https://docs.arize.com/~gitbook/image?url=https%3A%2F%2Fstorage.googleapis.com%2Farize-assets%2Fphoenix%2Fassets%2Fimages%2Fannotation_flow.gif&width=768&dpr=4&quality=100&sign=89bee7a9&sv=2)

Phoenix: Use Annotations to collect Human Feedback from your LLM App - YouTube

Arize AI

5.12K subscribers

[Phoenix: Use Annotations to collect Human Feedback from your LLM App](https://www.youtube.com/watch?v=20U6INQJyyU)

Arize AI

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

More videos

## More videos

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?t=1&v=20U6INQJyyU&embeds_referring_euri=https%3A%2F%2Fcdn.iframe.ly%2F)

0:01

0:01 / 9:06•Live

•

[Watch on YouTube](https://www.youtube.com/watch?v=20U6INQJyyU "Watch on YouTube")

[PreviousLog Evaluation Results](https://docs.arize.com/phoenix/tracing/how-to-tracing/llm-evaluations) [NextQuerying Spans](https://docs.arize.com/phoenix/tracing/how-to-tracing/extract-data-from-spans)

Last updated 2 months ago

This site uses cookies to deliver its service and to analyse traffic. By browsing this site, you accept the [privacy policy](https://arize.com/privacy-policy/).

AcceptReject

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)