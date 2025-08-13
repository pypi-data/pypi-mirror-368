# Health

Methods:

- <code title="get /health/">client.health.<a href="./src/fleet/resources/health.py">check</a>() -> object</code>

# Browsers

Types:

```python
from fleet.types import (
    VisitRequest,
    WaitUntil,
    BrowserDownloadFileResponse,
    BrowserGetMetadataResponse,
    BrowserLaunchResponse,
    BrowserVisitPageResponse,
)
```

Methods:

- <code title="get /browsers/">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">list</a>() -> object</code>
- <code title="delete /browsers/{browser_id}">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">close</a>(browser_id) -> object</code>
- <code title="post /browsers/{browser_id}/download">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">download_file</a>(browser_id, \*\*<a href="src/fleet/types/browser_download_file_params.py">params</a>) -> <a href="./src/fleet/types/browser_download_file_response.py">BrowserDownloadFileResponse</a></code>
- <code title="get /browsers/{browser_id}/metadata">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">get_metadata</a>(browser_id) -> <a href="./src/fleet/types/browser_get_metadata_response.py">BrowserGetMetadataResponse</a></code>
- <code title="post /browsers/">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">launch</a>(\*\*<a href="src/fleet/types/browser_launch_params.py">params</a>) -> <a href="./src/fleet/types/browser_launch_response.py">BrowserLaunchResponse</a></code>
- <code title="post /browsers/{browser_id}/scrape">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">scrape_page</a>(browser_id, \*\*<a href="src/fleet/types/browser_scrape_page_params.py">params</a>) -> object</code>
- <code title="post /browsers/{browser_id}/visit">client.browsers.<a href="./src/fleet/resources/browsers/browsers.py">visit_page</a>(browser_id, \*\*<a href="src/fleet/types/browser_visit_page_params.py">params</a>) -> <a href="./src/fleet/types/browser_visit_page_response.py">BrowserVisitPageResponse</a></code>

## Page

Types:

```python
from fleet.types.browsers import PageGetResponse, PageGetFullResponse, PageGetTextResponse
```

Methods:

- <code title="get /browsers/{browser_id}/page">client.browsers.page.<a href="./src/fleet/resources/browsers/page.py">get</a>(browser_id) -> <a href="./src/fleet/types/browsers/page_get_response.py">PageGetResponse</a></code>
- <code title="get /browsers/{browser_id}/page/full">client.browsers.page.<a href="./src/fleet/resources/browsers/page.py">get_full</a>(browser_id) -> <a href="./src/fleet/types/browsers/page_get_full_response.py">PageGetFullResponse</a></code>
- <code title="get /browsers/{browser_id}/page/text">client.browsers.page.<a href="./src/fleet/resources/browsers/page.py">get_text</a>(browser_id) -> <a href="./src/fleet/types/browsers/page_get_text_response.py">PageGetTextResponse</a></code>

## Responses

Types:

```python
from fleet.types.browsers import (
    ResponseClearResponse,
    ResponseGetAllResponse,
    ResponseGetFilteredResponse,
    ResponseGetLatestResponse,
    ResponseGetSummaryResponse,
    ResponseToggleTrackingResponse,
)
```

Methods:

- <code title="delete /browsers/{browser_id}/responses">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">clear</a>(browser_id) -> <a href="./src/fleet/types/browsers/response_clear_response.py">ResponseClearResponse</a></code>
- <code title="get /browsers/{browser_id}/responses">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">get_all</a>(browser_id) -> <a href="./src/fleet/types/browsers/response_get_all_response.py">ResponseGetAllResponse</a></code>
- <code title="get /browsers/{browser_id}/responses/filter">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">get_filtered</a>(browser_id, \*\*<a href="src/fleet/types/browsers/response_get_filtered_params.py">params</a>) -> <a href="./src/fleet/types/browsers/response_get_filtered_response.py">ResponseGetFilteredResponse</a></code>
- <code title="get /browsers/{browser_id}/responses/latest">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">get_latest</a>(browser_id) -> <a href="./src/fleet/types/browsers/response_get_latest_response.py">ResponseGetLatestResponse</a></code>
- <code title="get /browsers/{browser_id}/responses/summary">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">get_summary</a>(browser_id) -> <a href="./src/fleet/types/browsers/response_get_summary_response.py">ResponseGetSummaryResponse</a></code>
- <code title="post /browsers/{browser_id}/responses/toggle">client.browsers.responses.<a href="./src/fleet/resources/browsers/responses.py">toggle_tracking</a>(browser_id, \*\*<a href="src/fleet/types/browsers/response_toggle_tracking_params.py">params</a>) -> <a href="./src/fleet/types/browsers/response_toggle_tracking_response.py">ResponseToggleTrackingResponse</a></code>

# Scrape

Types:

```python
from fleet.types import (
    BrowserSelectionStrategy,
    ScrapeCleanupResponse,
    ScrapeGetBrowserStatsResponse,
)
```

Methods:

- <code title="post /scrape/cleanup">client.scrape.<a href="./src/fleet/resources/scrape/scrape.py">cleanup</a>(\*\*<a href="src/fleet/types/scrape_cleanup_params.py">params</a>) -> <a href="./src/fleet/types/scrape_cleanup_response.py">ScrapeCleanupResponse</a></code>
- <code title="get /scrape/browser-stats">client.scrape.<a href="./src/fleet/resources/scrape/scrape.py">get_browser_stats</a>() -> <a href="./src/fleet/types/scrape_get_browser_stats_response.py">ScrapeGetBrowserStatsResponse</a></code>

## Async

Types:

```python
from fleet.types.scrape import (
    AsyncScrapeRequest,
    JobStatus,
    AsyncCreateResponse,
    AsyncRetrieveResponse,
    AsyncListResponse,
    AsyncDeleteResponse,
)
```

Methods:

- <code title="post /scrape/async">client.scrape.async*.<a href="./src/fleet/resources/scrape/async*.py">create</a>(\*\*<a href="src/fleet/types/scrape/async_create_params.py">params</a>) -> <a href="./src/fleet/types/scrape/async_create_response.py">AsyncCreateResponse</a></code>
- <code title="get /scrape/async/{job_id}">client.scrape.async*.<a href="./src/fleet/resources/scrape/async*.py">retrieve</a>(job_id) -> <a href="./src/fleet/types/scrape/async_retrieve_response.py">AsyncRetrieveResponse</a></code>
- <code title="get /scrape/async">client.scrape.async*.<a href="./src/fleet/resources/scrape/async*.py">list</a>() -> <a href="./src/fleet/types/scrape/async_list_response.py">AsyncListResponse</a></code>
- <code title="delete /scrape/async/{job_id}">client.scrape.async*.<a href="./src/fleet/resources/scrape/async*.py">delete</a>(job_id) -> <a href="./src/fleet/types/scrape/async_delete_response.py">AsyncDeleteResponse</a></code>

## BrowserStrategy

Types:

```python
from fleet.types.scrape import BrowserStrategyResponse
```

Methods:

- <code title="get /scrape/browser-strategy">client.scrape.browser_strategy.<a href="./src/fleet/resources/scrape/browser_strategy.py">retrieve</a>() -> <a href="./src/fleet/types/scrape/browser_strategy_response.py">BrowserStrategyResponse</a></code>
- <code title="post /scrape/browser-strategy">client.scrape.browser_strategy.<a href="./src/fleet/resources/scrape/browser_strategy.py">update</a>(\*\*<a href="src/fleet/types/scrape/browser_strategy_update_params.py">params</a>) -> <a href="./src/fleet/types/scrape/browser_strategy_response.py">BrowserStrategyResponse</a></code>

# Profile

Types:

```python
from fleet.types import (
    NetworkCookie,
    NetworkRequestEvent,
    NetworkRequestFailedEvent,
    NetworkRequestFinishedEvent,
    NetworkResponseEvent,
    ProfileCaptureResponse,
    ProfileRunAgentResponse,
)
```

Methods:

- <code title="post /profile/capture">client.profile.<a href="./src/fleet/resources/profile.py">capture</a>(\*\*<a href="src/fleet/types/profile_capture_params.py">params</a>) -> <a href="./src/fleet/types/profile_capture_response.py">ProfileCaptureResponse</a></code>
- <code title="post /profile/agent">client.profile.<a href="./src/fleet/resources/profile.py">run_agent</a>(\*\*<a href="src/fleet/types/profile_run_agent_params.py">params</a>) -> <a href="./src/fleet/types/profile_run_agent_response.py">ProfileRunAgentResponse</a></code>

# Download

Types:

```python
from fleet.types import DownloadCreateJobResponse, DownloadGetJobStatusResponse
```

Methods:

- <code title="post /download">client.download.<a href="./src/fleet/resources/download.py">create_job</a>(\*\*<a href="src/fleet/types/download_create_job_params.py">params</a>) -> <a href="./src/fleet/types/download_create_job_response.py">DownloadCreateJobResponse</a></code>
- <code title="get /download/{job_id}">client.download.<a href="./src/fleet/resources/download.py">get_job_status</a>(job_id) -> <a href="./src/fleet/types/download_get_job_status_response.py">DownloadGetJobStatusResponse</a></code>

# Workflows

Types:

```python
from fleet.types import WorkflowDescribeResponse, WorkflowGetResultsResponse
```

Methods:

- <code title="get /workflows/describe/{workflow_id}">client.workflows.<a href="./src/fleet/resources/workflows/workflows.py">describe</a>(workflow_id) -> <a href="./src/fleet/types/workflow_describe_response.py">WorkflowDescribeResponse</a></code>
- <code title="get /workflows/results/{workflow_id}">client.workflows.<a href="./src/fleet/resources/workflows/workflows.py">get_results</a>(workflow_id) -> <a href="./src/fleet/types/workflow_get_results_response.py">WorkflowGetResultsResponse</a></code>

## Request

Types:

```python
from fleet.types.workflows import RequestCreateResponse
```

Methods:

- <code title="post /workflows/request/scrape">client.workflows.request.<a href="./src/fleet/resources/workflows/request.py">create</a>(\*\*<a href="src/fleet/types/workflows/request_create_params.py">params</a>) -> <a href="./src/fleet/types/workflows/request_create_response.py">RequestCreateResponse</a></code>
