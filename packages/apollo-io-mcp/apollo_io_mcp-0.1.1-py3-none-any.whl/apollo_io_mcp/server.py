import os
import httpx
from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Annotated, Dict, Any, Tuple, Union
from pydantic import Field, BaseModel

mcp = FastMCP("Apollo.io MCP Server")

# Apollo.io API configuration
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_BASE_URL = "https://api.apollo.io/api/v1"

if not APOLLO_API_KEY:
    raise ValueError("APOLLO_API_KEY environment variable is required")


class ApolloAPIClient:
    """Apollo.io API client for making authenticated requests."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = APOLLO_BASE_URL
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

    async def make_request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Union[Dict[str, Any], List, Tuple]] = None,
            data: Optional[Union[Dict[str, Any], List, Tuple]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Apollo.io API."""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=self.headers, json=data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()


# Initialize Apollo API client
apollo_client = ApolloAPIClient(APOLLO_API_KEY)


@mcp.tool(description="Use the Apollo.io People Enrichment endpoint to enrich data for a person.")
async def people_enrichment(
        first_name: Annotated[
            Optional[str], Field(description="The first name of the person, e.g., 'tim'")
        ] = None,
        last_name: Annotated[
            Optional[str], Field(description="The last name of the person, e.g., 'zheng'")
        ] = None,
        name: Annotated[
            Optional[str], Field(description="The full name of the person, e.g., 'tim zheng'")
        ] = None,
        email: Annotated[
            Optional[str], Field(description="The email address of the person, e.g., 'example@email.com'")
        ] = None,
        hashed_email: Annotated[
            Optional[str], Field(description="The MD5 or SHA-256 hashed email of the person")
        ] = None,
        organization_name: Annotated[
            Optional[str], Field(description="The name of the person's employer, e.g., 'apollo'")
        ] = None,
        domain: Annotated[
            Optional[str], Field(description="The domain of the person's employer, e.g., 'apollo.io'")
        ] = None,
        id: Annotated[
            Optional[str], Field(description="The Apollo ID of the person")
        ] = None,
        linkedin_url: Annotated[
            Optional[str], Field(description="The LinkedIn profile URL of the person")
        ] = None,
        reveal_personal_emails: Annotated[
            Optional[bool], Field(description="Whether to reveal personal emails; may consume credits")
        ] = False,
        reveal_phone_number: Annotated[
            Optional[bool], Field(description="Whether to reveal all phone numbers; requires webhook_url if true")
        ] = False,
        webhook_url: Annotated[
            Optional[str], Field(
                description="Webhook URL to receive phone number response if reveal_phone_number is true")
        ] = None,
):
    if reveal_phone_number and not webhook_url:
        return {"error": "`webhook_url` is required when `reveal_phone_number` is true."}

    endpoint = "/people/match"
    params = {
        "first_name": first_name,
        "last_name": last_name,
        "name": name,
        "email": email,
        "hashed_email": hashed_email,
        "organization_name": organization_name,
        "domain": domain,
        "id": id,
        "linkedin_url": linkedin_url,
        "reveal_personal_emails": str(reveal_personal_emails).lower(),
        "reveal_phone_number": str(reveal_phone_number).lower(),
        "webhook_url": webhook_url,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


class PersonDetails(BaseModel):
    first_name: Optional[str] = Field(description="The person's first name, e.g., 'tim'")
    last_name: Optional[str] = Field(description="The person's last name, e.g., 'zheng'")
    name: Optional[str] = Field(description="The full name, e.g., 'tim zheng'")
    email: Optional[str] = Field(description="Email address, e.g., 'example@email.com'")
    hashed_email: Optional[str] = Field(description="MD5 or SHA-256 hashed email")
    organization_name: Optional[str] = Field(description="Employer name, e.g., 'apollo'")
    domain: Optional[str] = Field(description="Employer domain, e.g., 'apollo.io'")
    id: Optional[str] = Field(description="Apollo ID, e.g., '587cf802f65125cad923a266'")
    linkedin_url: Optional[str] = Field(description="LinkedIn profile URL")


@mcp.tool(description="Use the Apollo.io Bulk People Enrichment endpoint to enrich data for up to 10 people.")
async def bulk_people_enrichment(
        details: Annotated[
            List[PersonDetails], Field(description="List of people to enrich (max 10)")
        ],
        reveal_personal_emails: Annotated[
            Optional[bool], Field(description="Whether to reveal personal emails (default: false)")
        ] = False,
        reveal_phone_number: Annotated[
            Optional[bool], Field(description="Whether to reveal phone numbers (default: false)")
        ] = False,
        webhook_url: Annotated[
            Optional[str], Field(description="Required if `reveal_phone_number` is true")
        ] = None,
):
    if len(details) > 10:
        return {"error": "You can enrich up to 10 people at once."}
    if reveal_phone_number and not webhook_url:
        return {"error": "`webhook_url` is required when `reveal_phone_number` is true."}

    endpoint = "/people/bulk_match"
    params = {
        "reveal_personal_emails": str(reveal_personal_emails).lower(),
        "reveal_phone_number": str(reveal_phone_number).lower(),
        "webhook_url": webhook_url,
    }
    params = {k: v for k, v in params.items() if v is not None}

    data = {
        "details": [person.dict(exclude_none=True) for person in details]
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=data
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Use the Apollo.io Organization Enrichment endpoint to enrich data for a company.")
async def organization_enrichment(
        domain: Annotated[
            str, Field(description="The domain of the company to enrich, e.g., 'apollo.io'")
        ]
):
    endpoint = "/organizations/enrich"
    params = {
        "domain": domain
    }

    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Use the Apollo.io Bulk Organization Enrichment endpoint to enrich data for up to 10 companies.")
async def bulk_organization_enrichment(
        domains: Annotated[
            List[str], Field(
                description="A list of company domains to enrich, max 10. e.g., ['apollo.io', 'microsoft.com']")
        ]
):
    if not domains:
        return {"error": "At least one domain is required."}
    if len(domains) > 10:
        return {"error": "You can enrich up to 10 domains at once."}

    endpoint = "/organizations/bulk_enrich"
    params = [("domains[]", domain) for domain in domains]  # Apollo expects repeated query key

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the People Search endpoint to find people in the Apollo database."
                " Several filters are available to help narrow your search."
)
async def people_search(
        person_titles: Annotated[
            Optional[List[str]],
            Field(description="Job titles held by the people you want to find.")
        ] = None,
        include_similar_titles: Annotated[
            Optional[bool],
            Field(description="Whether to include similar job titles in the search.")
        ] = None,
        q_keywords: Annotated[
            Optional[str],
            Field(description="A string of words over which we want to filter the results.")
        ] = None,
        person_locations: Annotated[
            Optional[List[str]],
            Field(description="The location where people live.")
        ] = None,
        person_seniorities: Annotated[
            Optional[List[str]],
            Field(description="The job seniority that people hold within their current employer.")
        ] = None,
        organization_locations: Annotated[
            Optional[List[str]],
            Field(description="The location of the company headquarters for a person's current employer.")
        ] = None,
        q_organization_domains_list: Annotated[
            Optional[List[str]],
            Field(description="The domain name for the person's employer.")
        ] = None,
        contact_email_status: Annotated[
            Optional[List[str]],
            Field(description="The email statuses for the people you want to find.")
        ] = None,
        organization_ids: Annotated[
            Optional[List[str]],
            Field(
                description="The Apollo IDs for the companies (employers) you want to include in your search results.")
        ] = None,
        organization_num_employees_ranges: Annotated[
            Optional[List[str]],
            Field(description="The number range of employees working for the person's current company.")
        ] = None,
        revenue_range_min: Annotated[
            Optional[int],
            Field(description="The minimum revenue the person's current employer generates.")
        ] = None,
        revenue_range_max: Annotated[
            Optional[int],
            Field(description="The maximum revenue the person's current employer generates.")
        ] = None,
        currently_using_all_of_technology_uids: Annotated[
            Optional[List[str]],
            Field(description="Find people based on all of the technologies their current employer uses.")
        ] = None,
        currently_using_any_of_technology_uids: Annotated[
            Optional[List[str]],
            Field(description="Find people based on any of the technologies their current employer uses.")
        ] = None,
        currently_not_using_any_of_technology_uids: Annotated[
            Optional[List[str]],
            Field(
                description="Exclude people from your search based on any of the technologies their current employer uses.")
        ] = None,
        q_organization_job_titles: Annotated[
            Optional[List[str]],
            Field(description="The job titles that are listed in active job postings at the person's current employer.")
        ] = None,
        organization_job_locations: Annotated[
            Optional[List[str]],
            Field(description="The locations of the jobs being actively recruited by the person's employer.")
        ] = None,
        organization_num_jobs_range_min: Annotated[
            Optional[int],
            Field(description="The minimum number of job postings active at the person's current employer.")
        ] = None,
        organization_num_jobs_range_max: Annotated[
            Optional[int],
            Field(description="The maximum number of job postings active at the person's current employer.")
        ] = None,
        organization_job_posted_at_range_min: Annotated[
            Optional[str],
            Field(description="The earliest date when jobs were posted by the person's current employer.")
        ] = None,
        organization_job_posted_at_range_max: Annotated[
            Optional[str],
            Field(description="The latest date when jobs were posted by the person's current employer.")
        ] = None,
        page: Annotated[
            Optional[int],
            Field(description="The page number of the Apollo data that you want to retrieve.")
        ] = None,
        per_page: Annotated[
            Optional[int],
            Field(description="The number of search results that should be returned for each page.")
        ] = None,
):
    endpoint = "/mixed_people/search"
    params = {
        "person_titles[]": person_titles,
        "include_similar_titles": include_similar_titles,
        "q_keywords": q_keywords,
        "person_locations[]": person_locations,
        "person_seniorities[]": person_seniorities,
        "organization_locations[]": organization_locations,
        "q_organization_domains_list[]": q_organization_domains_list,
        "contact_email_status[]": contact_email_status,
        "organization_ids[]": organization_ids,
        "organization_num_employees_ranges[]": organization_num_employees_ranges,
        "revenue_range[min]": revenue_range_min,
        "revenue_range[max]": revenue_range_max,
        "currently_using_all_of_technology_uids[]": currently_using_all_of_technology_uids,
        "currently_using_any_of_technology_uids[]": currently_using_any_of_technology_uids,
        "currently_not_using_any_of_technology_uids[]": currently_not_using_any_of_technology_uids,
        "q_organization_job_titles[]": q_organization_job_titles,
        "organization_job_locations[]": organization_job_locations,
        "organization_num_jobs_range[min]": organization_num_jobs_range_min,
        "organization_num_jobs_range[max]": organization_num_jobs_range_max,
        "organization_job_posted_at_range[min]": organization_job_posted_at_range_min,
        "organization_job_posted_at_range[max]": organization_job_posted_at_range_max,
        "page": page,
        "per_page": per_page,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


mcp.tool(description=(
    "Use the Organization Search endpoint to find companies in the Apollo database. "
    "Several filters are available to help narrow your search. "
    "Calling this endpoint consumes credits as part of your Apollo pricing plan. "
    "This feature is not accessible to Apollo users on free plans. "
    "This endpoint has a display limit of 50,000 records (100 per page, up to 500 pages). "
    "Add filters to narrow your search results."
))


async def organization_search(
        organization_num_employees_ranges: Annotated[
            Optional[List[str]], Field(
                None,
                alias="organization_num_employees_ranges[]",
                description=(
                        "The number range of employees working for the company. "
                        "Each range is a string with upper and lower numbers separated by a comma. "
                        "Examples: '1,10'; '250,500'; '10000,20000'"
                )
            )
        ] = None,
        organization_locations: Annotated[
            Optional[List[str]], Field(
                None,
                alias="organization_locations[]",
                description=(
                        "The location of the company headquarters (cities, states, countries). "
                        "Examples: 'texas'; 'tokyo'; 'spain'"
                )
            )
        ] = None,
        organization_not_locations: Annotated[
            Optional[List[str]], Field(
                None,
                alias="organization_not_locations[]",
                description=(
                        "Exclude companies based on headquarters location. "
                        "Examples: 'minnesota'; 'ireland'; 'seoul'"
                )
            )
        ] = None,
        revenue_range_min: Annotated[
            Optional[int], Field(
                None,
                alias="revenue_range[min]",
                description="Lower bound of organization revenue. Example: 300000"
            )
        ] = None,
        revenue_range_max: Annotated[
            Optional[int], Field(
                None,
                alias="revenue_range[max]",
                description="Upper bound of organization revenue. Example: 50000000"
            )
        ] = None,
        currently_using_any_of_technology_uids: Annotated[
            Optional[List[str]], Field(
                None,
                alias="currently_using_any_of_technology_uids[]",
                description=(
                        "Filter by technologies currently used by organization. "
                        "Examples: 'salesforce'; 'google_analytics'; 'wordpress_org'"
                )
            )
        ] = None,
        q_organization_keyword_tags: Annotated[
            Optional[List[str]], Field(
                None,
                alias="q_organization_keyword_tags[]",
                description="Filter by company keyword tags. Examples: 'mining'; 'sales strategy'"
            )
        ] = None,
        q_organization_name: Annotated[
            Optional[str], Field(
                None,
                description="Filter by company name (partial matches allowed). Example: 'apollo'"
            )
        ] = None,
        organization_ids: Annotated[
            Optional[List[str]], Field(
                None,
                alias="organization_ids[]",
                description="Filter by Apollo organization IDs. Example: '5e66b6381e05b4008c8331b8'"
            )
        ] = None,
        latest_funding_amount_range_min: Annotated[
            Optional[int], Field(
                None,
                alias="latest_funding_amount_range[min]",
                description="Min amount in most recent funding round. Examples: 5000000, 15000000"
            )
        ] = None,
        latest_funding_amount_range_max: Annotated[
            Optional[int], Field(
                None,
                alias="latest_funding_amount_range[max]",
                description="Max amount in most recent funding round."
            )
        ] = None,
        total_funding_range_min: Annotated[
            Optional[int], Field(
                None,
                alias="total_funding_range[min]",
                description="Min amount of all funding rounds combined."
            )
        ] = None,
        total_funding_range_max: Annotated[
            Optional[int], Field(
                None,
                alias="total_funding_range[max]",
                description="Max amount of all funding rounds combined."
            )
        ] = None,
        latest_funding_date_range_min: Annotated[
            Optional[str], Field(
                None,
                alias="latest_funding_date_range[min]",
                description="Earliest date of most recent funding round, e.g. '2025-07-25'"
            )
        ] = None,
        latest_funding_date_range_max: Annotated[
            Optional[str], Field(
                None,
                alias="latest_funding_date_range[max]",
                description="Latest date of most recent funding round, e.g. '2025-09-25'"
            )
        ] = None,
        q_organization_job_titles: Annotated[
            Optional[List[str]], Field(
                None,
                alias="q_organization_job_titles[]",
                description="Job titles listed in active job postings. Examples: 'sales manager'; 'research analyst'"
            )
        ] = None,
        organization_job_locations: Annotated[
            Optional[List[str]], Field(
                None,
                alias="organization_job_locations[]",
                description="Locations of active job postings. Examples: 'atlanta'; 'japan'"
            )
        ] = None,
        organization_num_jobs_range_min: Annotated[
            Optional[int], Field(
                None,
                alias="organization_num_jobs_range[min]",
                description="Min number of job postings active."
            )
        ] = None,
        organization_num_jobs_range_max: Annotated[
            Optional[int], Field(
                None,
                alias="organization_num_jobs_range[max]",
                description="Max number of job postings active."
            )
        ] = None,
        organization_job_posted_at_range_min: Annotated[
            Optional[str], Field(
                None,
                alias="organization_job_posted_at_range[min]",
                description="Earliest date jobs were posted, e.g. '2025-07-25'"
            )
        ] = None,
        organization_job_posted_at_range_max: Annotated[
            Optional[str], Field(
                None,
                alias="organization_job_posted_at_range[max]",
                description="Latest date jobs were posted, e.g. '2025-09-25'"
            )
        ] = None,
        page: Annotated[
            Optional[int], Field(
                None,
                description="Page number to retrieve. Example: 4"
            )
        ] = None,
        per_page: Annotated[
            Optional[int], Field(
                None,
                description="Number of results per page. Example: 10"
            )
        ] = None,
):
    # 组装 params，注意要用 API 参数名（带别名）
    raw_params = {
        "organization_num_employees_ranges[]": organization_num_employees_ranges,
        "organization_locations[]": organization_locations,
        "organization_not_locations[]": organization_not_locations,
        "revenue_range[min]": revenue_range_min,
        "revenue_range[max]": revenue_range_max,
        "currently_using_any_of_technology_uids[]": currently_using_any_of_technology_uids,
        "q_organization_keyword_tags[]": q_organization_keyword_tags,
        "q_organization_name": q_organization_name,
        "organization_ids[]": organization_ids,
        "latest_funding_amount_range[min]": latest_funding_amount_range_min,
        "latest_funding_amount_range[max]": latest_funding_amount_range_max,
        "total_funding_range[min]": total_funding_range_min,
        "total_funding_range[max]": total_funding_range_max,
        "latest_funding_date_range[min]": latest_funding_date_range_min,
        "latest_funding_date_range[max]": latest_funding_date_range_max,
        "q_organization_job_titles[]": q_organization_job_titles,
        "organization_job_locations[]": organization_job_locations,
        "organization_num_jobs_range[min]": organization_num_jobs_range_min,
        "organization_num_jobs_range[max]": organization_num_jobs_range_max,
        "organization_job_posted_at_range[min]": organization_job_posted_at_range_min,
        "organization_job_posted_at_range[max]": organization_job_posted_at_range_max,
        "page": page,
        "per_page": per_page,
    }
    # 清除 None 参数
    params = {k: v for k, v in raw_params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint="/mixed_companies/search",
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Use the Organization Job Postings endpoint to retrieve the current job postings for companies. "
        "This can help you identify companies that are growing headcount in areas that are strategically important for you. "
        "Calling this endpoint consumes credits as part of your Apollo pricing plan. "
        "This feature is not accessible to Apollo users on free plans. "
        "To protect Apollo's performance for all users, this endpoint has a display limit of 10,000 records."
))
async def organization_jobs_postings(
        organization_id: Annotated[
            str, Field(description=(
                    "The organization ID of the company for which you want to find job postings. "
                    "Each company in Apollo has a unique ID. "
                    "Example: '5e66b6381e05b4008c8331b8'"
            ))
        ],
        page: Annotated[
            Optional[int], Field(default=None, description="The page number of results to retrieve. Example: 4")
        ] = None,
        per_page: Annotated[
            Optional[int], Field(default=None, description="Number of results per page. Example: 10")
        ] = None,
):
    params = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page

    endpoint = f"/organizations/{organization_id}/job_postings"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Use the Create an Account endpoint to add a new account to your team's Apollo account. "
        "In Apollo terminology, an account is a company that your team has explicitly added to your database. "
        "Apollo does not deduplicate when creating accounts via API; to update use the Update an Account endpoint. "
        "This endpoint requires a master API key. Calling without it returns 403."
))
async def create_an_account(
        name: Annotated[
            Optional[str], Field(
                None,
                description="Name the account that you are creating. Example: 'The Irish Copywriters'"
            )
        ] = None,
        domain: Annotated[
            Optional[str], Field(
                None,
                description="The domain name for the account. Do not include www. Example: 'apollo.io'"
            )
        ] = None,
        owner_id: Annotated[
            Optional[str], Field(
                None,
                description="The ID for the account owner within your team's Apollo account. Example: '66302798d03b9601c7934ebf'"
            )
        ] = None,
        account_stage_id: Annotated[
            Optional[str], Field(
                None,
                description=(
                        "The Apollo ID for the account stage to assign the account. "
                        "Example: '6095a710bd01d100a506d4b9'"
                )
            )
        ] = None,
        phone: Annotated[
            Optional[str], Field(
                None,
                description=(
                        "The primary phone number for the account. "
                        "Examples: '555-303-1234'; '+44 7911 123456'"
                )
            )
        ] = None,
        raw_address: Annotated[
            Optional[str], Field(
                None,
                description=(
                        "The corporate location for the account. "
                        "Examples: 'Belfield, Dublin 4, Ireland'; 'Dallas, United States'"
                )
            )
        ] = None,
):
    params = {}
    if name is not None:
        params["name"] = name
    if domain is not None:
        params["domain"] = domain
    if owner_id is not None:
        params["owner_id"] = owner_id
    if account_stage_id is not None:
        params["account_stage_id"] = account_stage_id
    if phone is not None:
        params["phone"] = phone
    if raw_address is not None:
        params["raw_address"] = raw_address

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint="/accounts",
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Use the Update an Account endpoint to update existing accounts in your team's Apollo account. "
        "In Apollo terminology, an account is a company that your team has explicitly added to your database. "
        "To create a new account, use the Create an Account endpoint instead. "
        "This endpoint requires a master API key; without it, you'll get a 403 response."
))
async def update_an_account(
        account_id: Annotated[
            str, Field(
                ...,
                description=(
                        "The Apollo ID for the account that you want to update. "
                        "Example: '66e9abf95ac32901b20d1a0d'"
                )
            )
        ],
        name: Annotated[
            Optional[str], Field(
                None,
                description="Update the account's name. Example: 'The Fast Irish Copywriters'"
            )
        ] = None,
        domain: Annotated[
            Optional[str], Field(
                None,
                description="Update the domain name for the account. Example: 'apollo.io'"
            )
        ] = None,
        owner_id: Annotated[
            Optional[str], Field(
                None,
                description="Update the account owner ID. Example: '66302798d03b9601c7934ebf'"
            )
        ] = None,
        account_stage_id: Annotated[
            Optional[str], Field(
                None,
                description="Update the account stage ID. Example: '61b8e913e0f4d2012e3af74e'"
            )
        ] = None,
        raw_address: Annotated[
            Optional[str], Field(
                None,
                description="Update the corporate location. Example: 'Belfield, Dublin 4, Ireland'"
            )
        ] = None,
        phone: Annotated[
            Optional[str], Field(
                None,
                description="Update the primary phone number. Example: '+44 7911 123456'"
            )
        ] = None,
):
    params = {}
    if name is not None:
        params["name"] = name
    if domain is not None:
        params["domain"] = domain
    if owner_id is not None:
        params["owner_id"] = owner_id
    if account_stage_id is not None:
        params["account_stage_id"] = account_stage_id
    if raw_address is not None:
        params["raw_address"] = raw_address
    if phone is not None:
        params["phone"] = phone

    endpoint = f"/accounts/{account_id}"

    try:
        result = await apollo_client.make_request(
            method="PUT",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Search for Accounts endpoint to search for the account that have been added to your team's Apollo account.")
async def search_for_accounts(
        q_organization_name: Annotated[
            Optional[str],
            Field(description="Add keywords to narrow the search of the accounts in your team's Apollo account. "
                              "Example: 'apollo', 'microsoft', 'marketing'")
        ] = None,

        account_stage_ids: Annotated[
            Optional[List[str]],
            Field(alias="account_stage_ids[]", description="Apollo account stage IDs to include in search. "
                                                           "Example: ['61b8e913e0f4d2012e3af74e']")
        ] = None,

        sort_by_field: Annotated[
            Optional[str],
            Field(
                description="Sort by one of: `account_last_activity_date`, `account_created_at`, `account_updated_at`")
        ] = None,

        sort_ascending: Annotated[
            Optional[bool],
            Field(description="Set to `true` to sort in ascending order. Must be used with `sort_by_field`.")
        ] = False,

        page: Annotated[
            Optional[int],
            Field(description="The page number of the Apollo data to retrieve.")
        ] = None,

        per_page: Annotated[
            Optional[int],
            Field(description="Number of results per page.")
        ] = None,
):
    # 手动构造 params 字典并使用 alias 保持字段名一致
    params = {}

    if q_organization_name is not None:
        params["q_organization_name"] = q_organization_name
    if account_stage_ids is not None:
        params["account_stage_ids[]"] = account_stage_ids
    if sort_by_field is not None:
        params["sort_by_field"] = sort_by_field
    if sort_ascending is not None:
        params["sort_ascending"] = sort_ascending
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint="/accounts/search",
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Update Account Stage for Multiple Accounts endpoint to update the account stage for several account in your team's Apollo account.")
async def update_account_stage(
        account_ids: Annotated[
            List[str],
            Field(alias="account_ids[]", description="The Apollo IDs for the accounts you want to update. "
                                                     "Example: ['66e9abf95ac32901b20d1a0d']")
        ],
        account_stage_id: Annotated[
            str,
            Field(description="The Apollo ID of the account stage to assign to these accounts. "
                              "Example: '6095a710bd01d100a506d4b7'")
        ]
):
    endpoint = "/accounts/bulk_update"

    params = {
        "account_ids[]": account_ids,
        "account_stage_id": account_stage_id,
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Update Account Owner for Multiple Accounts endpoint to assign multiple accounts to a different user in your team's Apollo account.")
async def update_account_ownership(
        account_ids: Annotated[
            List[str],
            Field(alias="account_ids[]", description="The Apollo IDs for the accounts to assign to a new owner. "
                                                     "Example: ['66e9abf95ac32901b20d1a0d']")
        ],
        owner_id: Annotated[
            str,
            Field(description="The ID for the new account owner in your Apollo team. "
                              "Example: '66302798d03b9601c7934ebf'")
        ]
):
    endpoint = "/accounts/update_owners"

    params = {
        "account_ids[]": account_ids,
        "owner_id": owner_id,
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the List Accounts Stages endpoint to retrieve the IDs for the available account stages in your team's Apollo account.")
async def list_account_stages():
    endpoint = "/account_stages"

    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Use the Create a Contact endpoint to add a new contact to your team's Apollo account.")
async def create_a_contact(
        first_name: Annotated[
            Optional[str],
            Field(
                description="The first name of the contact you want to create. This should be a human-readable name. Example: `Tim`")
        ] = None,
        last_name: Annotated[
            Optional[str],
            Field(
                description="The last name of the contact you want to create. This should be a human-readable name. Example: `Zheng`")
        ] = None,
        organization_name: Annotated[
            Optional[str],
            Field(
                description="The name of the contact's employer (company). This should be the current employer. Example: `apollo`")
        ] = None,
        title: Annotated[
            Optional[str],
            Field(description="The current job title that the contact holds. Example: `senior research analyst`")
        ] = None,
        account_id: Annotated[
            Optional[str],
            Field(
                description="The Apollo ID for the account to which you want to assign the contact. Example: `63f53afe4ceeca00016bdd2f`")
        ] = None,
        email: Annotated[
            Optional[str],
            Field(description="The email address of the contact. Example: `example@email.com`")
        ] = None,
        website_url: Annotated[
            Optional[str],
            Field(
                description="The corporate website URL for the contact's current employer. Examples: `https://www.apollo.io/`; `https://www.microsoft.com/`")
        ] = None,
        label_names: Annotated[
            Optional[List[str]],
            Field(
                description="Add the contact to lists within your team's Apollo account. Examples: `2024 big marketing conference attendees`; `inbound contact`; `smb clients`")
        ] = None,
        contact_stage_id: Annotated[
            Optional[str],
            Field(
                description="The Apollo ID for the contact stage to which you want to assign the contact. Example: `6095a710bd01d100a506d4ae`")
        ] = None,
        present_raw_address: Annotated[
            Optional[str],
            Field(
                description="The personal location for the contact. Examples: `Atlanta, United States`; `Tokyo, Japan`; `Saint Petersburg, Russia`")
        ] = None,
        direct_phone: Annotated[
            Optional[str],
            Field(description="The primary phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        corporate_phone: Annotated[
            Optional[str],
            Field(
                description="The work/office phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        mobile_phone: Annotated[
            Optional[str],
            Field(description="The mobile phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        home_phone: Annotated[
            Optional[str],
            Field(description="The home phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        other_phone: Annotated[
            Optional[str],
            Field(
                description="An unknown type of phone number or an alternative phone number. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
):
    endpoint = "/contacts"

    # 构造参数（过滤掉 None）
    params = {
        "first_name": first_name,
        "last_name": last_name,
        "organization_name": organization_name,
        "title": title,
        "account_id": account_id,
        "email": email,
        "website_url": website_url,
        "label_names[]": label_names,
        "contact_stage_id": contact_stage_id,
        "present_raw_address": present_raw_address,
        "direct_phone": direct_phone,
        "corporate_phone": corporate_phone,
        "mobile_phone": mobile_phone,
        "home_phone": home_phone,
        "other_phone": other_phone,
    }

    # 过滤掉 None 的字段
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Use the Update a Contact endpoint to update existing contacts in your team's Apollo account.")
async def update_a_contact(
        contact_id: Annotated[
            str,
            Field(
                description="The Apollo ID for the contact that you want to update. Example: `66e34b81740c50074e3d1bd4`")
        ],
        first_name: Annotated[
            Optional[str],
            Field(description="Update the contact's first name. This should be a human-readable name. Example: `Tim`")
        ] = None,
        last_name: Annotated[
            Optional[str],
            Field(description="Update the contact's last name. This should be a human-readable name. Example: `Zheng`")
        ] = None,
        organization_name: Annotated[
            Optional[str],
            Field(description="Update the name of the contact's employer (company). Example: `apollo`")
        ] = None,
        title: Annotated[
            Optional[str],
            Field(description="Update the job title that the contact holds. Example: `senior research analyst`")
        ] = None,
        account_id: Annotated[
            Optional[str],
            Field(
                description="The Apollo ID to update the account to which the contact is assigned. Example: `63f53afe4ceeca00016bdd2f`")
        ] = None,
        email: Annotated[
            Optional[str],
            Field(description="Update the email address of the contact. Example: `example@email.com`")
        ] = None,
        website_url: Annotated[
            Optional[str],
            Field(
                description="Update the corporate website URL for the contact's current employer. Examples: `https://www.apollo.io/`; `https://www.microsoft.com/`")
        ] = None,
        label_names: Annotated[
            Optional[List[str]],
            Field(
                description="Update the lists that the contact belongs to within your team's Apollo account. Examples: `2024 big marketing conference attendees`; `inbound contact`; `smb clients`")
        ] = None,
        contact_stage_id: Annotated[
            Optional[str],
            Field(
                description="The Apollo ID to update the contact stage to which the contact is assigned. Example: `6095a710bd01d100a506d4af`")
        ] = None,
        present_raw_address: Annotated[
            Optional[str],
            Field(
                description="Update the personal location for the contact. Examples: `Atlanta, United States`; `Tokyo, Japan`; `Saint Petersburg, Russia`")
        ] = None,
        direct_phone: Annotated[
            Optional[str],
            Field(
                description="Update the primary phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        corporate_phone: Annotated[
            Optional[str],
            Field(
                description="Update the work/office phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        mobile_phone: Annotated[
            Optional[str],
            Field(
                description="Update the mobile phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        home_phone: Annotated[
            Optional[str],
            Field(
                description="Update the home phone number for the contact. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
        other_phone: Annotated[
            Optional[str],
            Field(
                description="Update an unknown type of phone number or an alternative phone number. Examples: `555-303-1234`; `+44 7911 123456`")
        ] = None,
):
    endpoint = f"/contacts/{contact_id}"

    params = {
        "first_name": first_name,
        "last_name": last_name,
        "organization_name": organization_name,
        "title": title,
        "account_id": account_id,
        "email": email,
        "website_url": website_url,
        "label_names[]": label_names,
        "contact_stage_id": contact_stage_id,
        "present_raw_address": present_raw_address,
        "direct_phone": direct_phone,
        "corporate_phone": corporate_phone,
        "mobile_phone": mobile_phone,
        "home_phone": home_phone,
        "other_phone": other_phone,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="PUT",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Search for Contacts endpoint to search for the contacts that have been added to your team's Apollo account.")
async def search_for_contacts(
        q_keywords: Annotated[
            Optional[str],
            Field(
                description="Add keywords to narrow the search of the contacts in your team's Apollo account. Examples: `tim zheng`; `senior research analyst`; `microsoft`")
        ] = None,
        contact_stage_ids: Annotated[
            Optional[List[str]],
            Field(
                description="The Apollo IDs for the contact stages that you want to include in your search results. Example: `6095a710bd01d100a506d4ae`")
        ] = None,
        sort_by_field: Annotated[
            Optional[str],
            Field(description=(
                    "Sort the matching contacts by 1 of the following options: "
                    "`contact_last_activity_date`, `contact_email_last_opened_at`, "
                    "`contact_email_last_clicked_at`, `contact_created_at`, `contact_updated_at`"
            ))
        ] = None,
        sort_ascending: Annotated[
            Optional[bool],
            Field(description=(
                    "Set to `true` to sort the matching contacts in ascending order. "
                    "Must be used with `sort_by_field`. Example: `true`"
            ))
        ] = None,
        per_page: Annotated[
            Optional[int],
            Field(description="The page number of the Apollo data that you want to retrieve. Example: `4`")
        ] = None,
        page: Annotated[
            Optional[int],
            Field(description="The number of search results that should be returned for each page. Example: `10`")
        ] = None,
):
    endpoint = "/contacts/search"
    params = {
        "q_keywords": q_keywords,
        "contact_stage_ids[]": contact_stage_ids,
        "sort_by_field": sort_by_field,
        "sort_ascending": str(sort_ascending).lower() if sort_ascending is not None else None,
        "per_page": per_page,
        "page": page,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Update Contact Stage for Multiple Contacts endpoint to update the contact stage for several contacts in your team's Apollo account.")
async def update_contact_stage(
        contact_ids: Annotated[
            List[str],
            Field(
                description="The Apollo IDs for the contacts that you want to update. Example: `66e34b81740c50074e3d1bd4`")
        ],
        contact_stage_id: Annotated[
            str,
            Field(
                description="The Apollo ID for the contact stage to which you want to assign the contacts. Example: `6095a710bd01d100a506d4af`")
        ],
):
    endpoint = "/contacts/update_stages"

    params = {
        "contact_ids[]": contact_ids,
        "contact_stage_id": contact_stage_id,
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Use the Update Contact Owner for Multiple Contacts endpoint to assign multiple contacts to a different user in your team's Apollo account.")
async def update_contact_ownership(
        contact_ids: Annotated[
            List[str],
            Field(
                description="The Apollo IDs for the contacts that you want assign to an owner. Example: `66e34b81740c50074e3d1bd4`")
        ],
        owner_id: Annotated[
            str,
            Field(
                description="The ID for the contact owner within your team's Apollo account. Example: `66302798d03b9601c7934ebf`")
        ],
):
    endpoint = "/contacts/update_owners"

    params = {
        "contact_ids[]": contact_ids,
        "owner_id": owner_id,
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve the list of available contact stages in your Apollo team's account. "
        "Contact stage IDs can be used to update individual contacts or bulk update contact stages via the Apollo API."
))
async def list_contact_stages():
    """
    Use the List Contact Stages endpoint to get all contact stages with their IDs and metadata.
    """
    endpoint = "/contact_stages"
    try:
        result = await apollo_client.make_request(method="GET", endpoint=endpoint)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Create new deals in an Apollo account to track activity including value, owners, and stages. "
        "Requires a master API key."
))
async def create_deal(
        name: Annotated[str, Field(description="Human-readable name for the deal, e.g., 'Massive Q3 Deal'")],
        owner_id: Annotated[Optional[str], Field(description=(
                "ID of the deal owner in your Apollo team. Use 'Get a List of Users' endpoint to retrieve IDs. "
                "Example: '66302798d03b9601c7934ebf'"
        ))] = None,
        account_id: Annotated[Optional[str], Field(description=(
                "ID of the account (company) in Apollo for the deal. Use 'Organization Search' endpoint to find IDs. "
                "Example: '5e66b6381e05b4008c8331b8'"
        ))] = None,
        amount: Annotated[Optional[str], Field(description=(
                "Monetary value of the deal without commas or currency symbols. Currency set by Apollo account settings. "
                "Example: '55123478' (means $55,123,478 if USD)"
        ))] = None,
        opportunity_stage_id: Annotated[Optional[str], Field(description=(
                "ID of the deal stage in your Apollo account. Use 'List Deal Stages' endpoint to find IDs. "
                "Example: '6095a710bd01d100a506d4bd'"
        ))] = None,
        closed_date: Annotated[Optional[str], Field(description=(
                "Estimated close date in 'YYYY-MM-DD' format. Can be past or future date. Example: '2025-10-30'"
        ))] = None,
):
    endpoint = "/opportunities"
    params = {
        "name": name,
        "owner_id": owner_id,
        "account_id": account_id,
        "amount": amount,
        "opportunity_stage_id": opportunity_stage_id,
        "closed_date": closed_date,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Use the List All Deals endpoint to retrieve every deal created for your team's Apollo account.")
async def list_all_deals(
        sort_by_field: Annotated[
            Optional[str],
            Field(description="Sort the tasks by one of: `amount`, `is_closed`, `is_won`. Example: `amount`")
        ] = None,
        page: Annotated[
            Optional[int],
            Field(description="The page number of the Apollo data to retrieve. Example: `4`")
        ] = None,
        per_page: Annotated[
            Optional[int],
            Field(description="The number of search results returned per page. Example: `10`")
        ] = None,
):
    endpoint = "/opportunities/search"
    params = {
        "sort_by_field": sort_by_field,
        "page": page,
        "per_page": per_page,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Retrieve complete details about a deal within your team's Apollo account.")
async def view_deal(
        opportunity_id: Annotated[
            str, Field(description="The unique ID of the deal to view. Example: '66e09ea8e3cfcf01b2208ec7'")],
):
    endpoint = f"/opportunities/{opportunity_id}"
    try:
        result = await apollo_client.make_request(method="GET", endpoint=endpoint)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(description="Update the details of an existing deal within your team's Apollo account.")
async def update_deal(
        opportunity_id: Annotated[
            str, Field(description="The unique ID of the deal to update. Example: '66e09ea8e3cfcf01b2208ec7'")],
        owner_id: Optional[
            Annotated[str, Field(description="ID for the deal owner within your team's Apollo account.")]] = None,
        name: Optional[
            Annotated[str, Field(description="Human-readable name of the deal. Example: 'Massive Q3 Deal'")]] = None,
        amount: Optional[
            Annotated[str, Field(description="Monetary value of the deal. No commas or currency symbols.")]] = None,
        opportunity_stage_id: Optional[Annotated[str, Field(description="ID of the deal stage.")]] = None,
        closed_date: Optional[Annotated[str, Field(description="Estimated close date, format YYYY-MM-DD.")]] = None,
        is_closed: Optional[Annotated[bool, Field(description="Set true to mark the deal as closed.")]] = None,
        is_won: Optional[Annotated[bool, Field(description="Set true to mark the deal as won.")]] = None,
        source: Optional[
            Annotated[str, Field(description="Source of the deal. Example: '2024 InfoSec Conference'")]] = None,
        account_id: Optional[
            Annotated[str, Field(description="ID of the account/company associated with the deal.")]] = None,
):
    endpoint = f"/opportunities/{opportunity_id}"
    params = {
        "owner_id": owner_id,
        "name": name,
        "amount": amount,
        "opportunity_stage_id": opportunity_stage_id,
        "closed_date": closed_date,
        "is_closed": is_closed,
        "is_won": is_won,
        "source": source,
        "account_id": account_id,
    }
    # 过滤掉 None 参数
    params = {k: v for k, v in params.items() if v is not None}
    try:
        result = await apollo_client.make_request(method="PATCH", endpoint=endpoint, params=params)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(description="Retrieve all deal stages available in your team's Apollo account.")
async def list_deal_stages():
    endpoint = "/opportunity_stages"
    try:
        result = await apollo_client.make_request(method="GET", endpoint=endpoint)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(description=(
        "Search for sequences created in your team's Apollo account. Requires a master API key "
        "(see https://docs.apollo.io/docs/create-api-key). Not available on free plans."
))
async def search_for_sequences(
        q_name: Annotated[
            Optional[str], Field(description=(
                    "Keywords to filter sequences by name. Matches part of the sequence's name. "
                    "Example: 'marketing conference attendees'"
            ))
        ] = None,
        page: Annotated[
            Optional[str], Field(description=(
                    "Page number of results to retrieve. Use with 'per_page' for pagination. Example: '4'"
            ))
        ] = None,
        per_page: Annotated[
            Optional[str], Field(description=(
                    "Number of results per page to return. Use with 'page' for pagination. Example: '10'"
            ))
        ] = None,
):
    endpoint = "/emailer_campaigns/search"
    params = {
        "q_name": q_name,
        "page": page,
        "per_page": per_page,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


mcp.tool(description=(
    "Add contacts to an existing sequence in your team's Apollo account. "
    "Requires a master API key (see https://docs.apollo.io/docs/create-api-key). "
    "Only contacts can be added to sequences."
))


async def add_contacts_to_sequence(
        emailer_campaign_id: Annotated[
            str, Field(description="Same ID as the sequence_id. Example: '66e9e215ece19801b219997f'")
        ],
        sequence_id: Annotated[
            str, Field(description=(
                    "Apollo ID of the sequence to add contacts to. "
                    "Find via the Search for Sequences endpoint. Example: '66e9e215ece19801b219997f'"
            ))
        ],
        contact_ids: Annotated[
            List[str], Field(description=(
                    "List of Apollo contact IDs to add to the sequence. "
                    "Find via the Search for Contacts endpoint. Example: ['66e34b81740c50074e3d1bd4']"
            ))
        ],
        send_email_from_email_account_id: Annotated[
            str, Field(description=(
                    "Apollo ID of the email account to send emails from. "
                    "Find via the Get a List of Email Accounts endpoint. Example: '6633baaece5fbd01c791d7ca'"
            ))
        ],
        sequence_no_email: Annotated[
            Optional[bool], Field(default=False, description="Add contacts without email addresses if true.")
        ] = False,
        sequence_unverified_email: Annotated[
            Optional[bool], Field(default=False, description="Add contacts with unverified emails if true.")
        ] = False,
        sequence_job_change: Annotated[
            Optional[bool], Field(default=False, description="Add contacts even if they recently changed jobs if true.")
        ] = False,
        sequence_active_in_other_campaigns: Annotated[
            Optional[bool], Field(default=False, description=(
                    "Add contacts even if active in other sequences (including paused) if true."
            ))
        ] = False,
        sequence_finished_in_other_campaigns: Annotated[
            Optional[bool], Field(default=False, description=(
                    "Add contacts even if marked 'finished' in other sequences if true."
            ))
        ] = False,
        user_id: Annotated[
            Optional[str], Field(description=(
                    "User ID of the person adding contacts. "
                    "Find via the Get a List of Users endpoint. Example: '66302798d03b9601c7934ebf'"
            ))
        ] = None,
):
    endpoint = f"/emailer_campaigns/{sequence_id}/add_contact_ids"
    params = {
        "emailer_campaign_id": emailer_campaign_id,
        "contact_ids[]": contact_ids,
        "send_email_from_email_account_id": send_email_from_email_account_id,
        "sequence_no_email": str(sequence_no_email).lower(),
        "sequence_unverified_email": str(sequence_unverified_email).lower(),
        "sequence_job_change": str(sequence_job_change).lower(),
        "sequence_active_in_other_campaigns": str(sequence_active_in_other_campaigns).lower(),
        "sequence_finished_in_other_campaigns": str(sequence_finished_in_other_campaigns).lower(),
    }
    if user_id:
        params["user_id"] = user_id

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Update the status of contacts in one or more sequences by marking them as finished, removing them, or stopping their progress. "
        "Requires a master API key (see https://docs.apollo.io/docs/create-api-key)."
))
async def update_contact_status_sequence(
        emailer_campaign_ids: Annotated[
            List[str], Field(description=(
                    "Apollo IDs of the sequences to update. Updates apply across all listed sequences. "
                    "Find via Search for Sequences endpoint. Example: ['66e9e215ece19801b219997f']"
            ))
        ],
        contact_ids: Annotated[
            List[str], Field(description=(
                    "Apollo IDs of the contacts whose status will be updated. "
                    "Find via Search for Contacts endpoint. Example: ['66e34b81740c50074e3d1bd4']"
            ))
        ],
        mode: Annotated[
            str, Field(description=(
                    "Update mode - one of: 'mark_as_finished' (mark contacts finished), "
                    "'remove' (remove contacts from sequences), or 'stop' (halt contacts' sequence progress)."
            ))
        ],
):
    endpoint = "/emailer_campaigns/remove_or_stop_contact_ids"
    params = {
        "emailer_campaign_ids[]": emailer_campaign_ids,
        "contact_ids[]": contact_ids,
        "mode": mode,
    }

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


mcp.tool(description=(
    "Create tasks in Apollo for you and your team. Tasks track upcoming actions like emailing or calling contacts. "
    "Requires a master API key (see https://docs.apollo.io/docs/create-api-key). "
    "Apollo does not deduplicate tasks created via the API. Not available on free plans."
))


async def create_task(
        user_id: Annotated[
            str, Field(description=(
                    "ID of the task owner within your team's Apollo account. "
                    "Find via Get a List of Users endpoint. Example: '66302798d03b9601c7934ebf'"
            ))
        ],
        contact_ids: Annotated[
            List[str], Field(description=(
                    "Apollo IDs of contacts for whom tasks are created. "
                    "Creates one task per contact with the same details. "
                    "Find via Search for Contacts endpoint. Example: ['66e34b81740c50074e3d1bd4']"
            ))
        ],
        priority: Annotated[
            str, Field(description="Task priority: 'high', 'medium', or 'low'")
        ],
        due_at: Annotated[
            str, Field(description=(
                    "ISO 8601 date-time string for when the task is due. "
                    "Apollo uses GMT by default. Example: '2025-02-15T08:10:30Z'"
            ))
        ],
        type: Annotated[
            str, Field(description=(
                    "Task type indicating the action required: "
                    "'call', 'outreach_manual_email', 'linkedin_step_connect', 'linkedin_step_message', "
                    "'linkedin_step_view_profile', 'linkedin_step_interact_post', or 'action_item'"
            ))
        ],
        status: Annotated[
            str, Field(description=(
                    "Task status. Use 'scheduled' for future tasks, 'completed' or 'archived' for finished ones. Example: 'scheduled'"
            ))
        ],
        note: Annotated[
            Optional[str], Field(default=None, description=(
                    "Optional description providing context for the task. Example: "
                    "'This contact expressed interest in the Sequences feature specifically.'"
            ))
        ] = None,
):
    endpoint = "/tasks/bulk_create"
    params = {
        "user_id": user_id,
        "contact_ids[]": contact_ids,
        "priority": priority,
        "due_at": due_at,
        "type": type,
        "status": status,
    }
    if note is not None:
        params["note"] = note

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Search for tasks created by your team in Apollo. Results are limited to 50,000 records "
        "(100 per page, up to 500 pages). Use filters to narrow results. Requires a master API key "
        "(see https://docs.apollo.io/docs/create-api-key). Not available on free plans."
))
async def search_tasks(
        sort_by_field: Annotated[
            Optional[str], Field(description=(
                    "Sort tasks by: 'task_due_at' (future-dated first) or 'task_priority' (highest priority first)."
            ))
        ] = None,
        open_factor_names: Annotated[
            Optional[List[str]], Field(description=(
                    "Enter 'task_types' to get count of tasks by type included in response."
            ))
        ] = None,
        page: Annotated[
            Optional[int], Field(description=(
                    "Page number of results to retrieve. Use with 'per_page' for pagination. Example: 4"
            ))
        ] = None,
        per_page: Annotated[
            Optional[int], Field(description=(
                    "Number of results per page. Use with 'page' for pagination. Example: 10"
            ))
        ] = None,
):
    endpoint = "/tasks/search"
    params = {
        "sort_by_field": sort_by_field,
        "page": page,
        "per_page": per_page,
    }
    if open_factor_names is not None:
        params["open_factor_names[]"] = open_factor_names

    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="POST",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve the IDs of all users (teammates) in your Apollo account. "
        "These IDs can be used in endpoints like Create a Deal, Create an Account, and Create a Task. "
        "Requires a master API key (see https://docs.apollo.io/docs/create-api-key). Not available on free plans."
))
async def get_a_list_of_users(
        page: Annotated[
            Optional[int], Field(description=(
                    "Page number of results to retrieve. Use with 'per_page' for pagination. Example: 4"
            ))
        ] = None,
        per_page: Annotated[
            Optional[int], Field(description=(
                    "Number of results per page. Use with 'page' for pagination. Example: 10"
            ))
        ] = None,
):
    endpoint = "/users/search"
    params = {
        "page": page,
        "per_page": per_page,
    }
    params = {k: v for k, v in params.items() if v is not None}

    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve information about the linked email inboxes your teammates use in Apollo. "
        "Returns IDs for linked email accounts usable in Add Contacts to a Sequence. "
        "Requires a master API key (see https://docs.apollo.io/docs/create-api-key)."
))
async def get_a_list_of_email_accounts():
    endpoint = "/email_accounts"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=None,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve information about every list and tag created in your Apollo account. "
        "Useful to check available lists before creating contacts. "
        "Requires a master API key (see https://docs.apollo.io/docs/create-api-key)."
))
async def get_a_list_of_all_liststags():
    endpoint = "/labels"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=None,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve information about all custom fields created in your Apollo account. "
        "Requires a master API key (see https://docs.apollo.io/docs/create-api-key)."
))
async def get_a_list_of_all_custom_fields():
    endpoint = "/typed_custom_fields"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=None,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve details for an organization by its Apollo ID. "
        "Find IDs via the Organization Search endpoint."
))
async def get_organizations_id(
        id: Annotated[str, Field(description=(
                "Apollo ID of the organization to retrieve. Example: '5e66b6381e05b4008c8331b8'"
        ))]
):
    endpoint = f"/organizations/{id}"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=None,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Retrieve details for an account by its Apollo ID. "
        "Find IDs via the Search for Accounts endpoint."
))
async def get_accounts_id(
        id: Annotated[str, Field(description=(
                "Apollo ID of the account to retrieve. Example: '6518c6184f20350001a0b9c0'"
        ))]
):
    endpoint = f"/accounts/{id}"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=None,
            data=None
        )
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description=(
        "Search phone calls in your Apollo account with optional filters such as date range, "
        "call duration, inbound/outbound, users involved, contact labels, call purposes and outcomes, "
        "keywords, and pagination. Requires a master API key."
))
async def search_phone_calls(
        date_range_max: Annotated[Optional[str], Field(
            description="Upper bound of date range (YYYY-MM-DD), must be after date_range_min"
        )] = None,
        date_range_min: Annotated[Optional[str], Field(
            description="Lower bound of date range (YYYY-MM-DD), must be before date_range_max"
        )] = None,
        duration_max: Annotated[Optional[int], Field(
            description="Max call duration in seconds, must be >= duration_min"
        )] = None,
        duration_min: Annotated[Optional[int], Field(
            description="Min call duration in seconds, must be <= duration_max"
        )] = None,
        inbound: Annotated[Optional[str], Field(
            description="Search calls by direction: 'incoming' or 'outgoing'"
        )] = None,
        user_ids: Annotated[Optional[List[str]], Field(
            description="Filter calls involving specific user IDs"
        )] = None,
        contact_label_ids: Annotated[Optional[List[str]], Field(
            description="Filter calls involving specific contact label IDs"
        )] = None,
        phone_call_purpose_ids: Annotated[Optional[List[str]], Field(
            description="Filter calls by purpose IDs"
        )] = None,
        phone_call_outcome_ids: Annotated[Optional[List[str]], Field(
            description="Filter calls by outcome IDs"
        )] = None,
        q_keywords: Annotated[Optional[str], Field(
            description="Keywords to narrow search"
        )] = None,
        page: Annotated[Optional[int], Field(
            description="Page number for paginated results"
        )] = None,
        per_page: Annotated[Optional[int], Field(
            description="Number of results per page"
        )] = None,
):
    params = {}
    if date_range_max:
        params["date_range[max]"] = date_range_max
    if date_range_min:
        params["date_range[min]"] = date_range_min
    if duration_max is not None:
        params["duration[max]"] = duration_max
    if duration_min is not None:
        params["duration[min]"] = duration_min
    if inbound:
        params["inbound"] = inbound
    if user_ids:
        params["user_ids[]"] = user_ids
    if contact_label_ids:
        params["contact_label_ids[]"] = contact_label_ids
    if phone_call_purpose_ids:
        params["phone_call_purpose_ids[]"] = phone_call_purpose_ids
    if phone_call_outcome_ids:
        params["phone_call_outcome_ids[]"] = phone_call_outcome_ids
    if q_keywords:
        params["q_keywords"] = q_keywords
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page

    endpoint = "/phone_calls/search"
    try:
        result = await apollo_client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            data=None
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(description="Get stats for a specific outreach email by its ID.")
async def get_emailstats(
        id: Annotated[
            str,
            Field(
                description=(
                        "The ID for the email you want to view. "
                        "Each outreach email in Apollo is assigned a unique ID. "
                        "To find email IDs, call the Search for Outreach Emails endpoint and identify the `id` value for the email. "
                        "Example: `684b2203a2ce950021cbf730`"
                )
            )
        ]
):
    endpoint = f"/emailer_messages/{id}/activities"
    try:
        result = await apollo_client.make_request(method="GET", endpoint=endpoint)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(
    description="Search outreach emails with various filters such as status, reply sentiment, user, date range, and more.")
async def emailer_messages_search(
        emailer_message_stats: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Find emails based on their current status, such as whether they were delivered or opened. "
                        "Possible values include: delivered, scheduled, drafted, not_opened, opened, clicked, unsubscribed, demoed, bounced, spam_blocked, failed_other."
                )
            )
        ] = None,
        emailer_message_reply_classes: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Find emails based on the response sentiment of the recipient. "
                        "Possible values include: willing_to_meet, follow_up_question, person_referral, out_of_office, already_left_company_or_not_right_person, not_interested, unsubscribe, none_of_the_above."
                )
            )
        ] = None,
        user_ids: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Find emails sent by specific users in your team's Apollo account. "
                        "Use the Get a List of Users endpoint to retrieve IDs. Example: `66302798d03b9601c7934ebf`"
                )
            )
        ] = None,
        email_account_id_and_aliases: Annotated[
            Optional[str], Field(description="Filter by email account ID and its aliases.")
        ] = None,
        emailer_campaign_ids: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Search for emails included in specific sequences in Apollo. "
                        "Use the Search for Sequences endpoint to find sequence IDs. Example: `66e9e215ece19801b219997f`"
                )
            )
        ] = None,
        not_emailer_campaign_ids: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Exclude emails from specific sequences. "
                        "Use the Search for Sequences endpoint to find sequence IDs. Example: `66e9e215ece19801b219997f`"
                )
            )
        ] = None,
        emailer_message_date_range_mode: Annotated[
            Optional[str],
            Field(
                description=(
                        "Find emails based on date mode. Options: due_at (scheduled delivery date), completed_at (actual delivery date)."
                )
            )
        ] = None,
        emailerMessageDateRange_max: Annotated[
            Optional[str],
            Field(
                description=(
                        "Upper bound of the date range, format YYYY-MM-DD. "
                        "Must be used with emailerMessageDateRange_min and emailer_message_date_range_mode."
                )
            )
        ] = None,
        emailerMessageDateRange_min: Annotated[
            Optional[str],
            Field(
                description=(
                        "Lower bound of the date range, format YYYY-MM-DD. "
                        "Must be used with emailerMessageDateRange_max and emailer_message_date_range_mode."
                )
            )
        ] = None,
        not_sent_reason_cds: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Find emails based on reasons they were not sent. Possible values include: "
                        "contact_stage_safeguard, same_account_reply, account_stage_safeguard, email_unverified, snippets_missing, personalized_opener_missing, thread_reply_original_email_missing, no_active_email_account, email_format_invalid, ownership_permission, email_service_provider_delivery_failure, sendgrid_dropped_email, mailgun_dropped_email, gdpr_compliance, not_valid_hard_bounce_detected, other_safeguard, new_job_change_detected, email_on_global_bounce_list."
                )
            )
        ] = None,
        q_keywords: Annotated[
            Optional[str],
            Field(
                description=(
                        "Add keywords to narrow the search of emails. Keywords should match email content or sender."
                )
            )
        ] = None,
        page: Annotated[
            Optional[int],
            Field(description="Page number for paginated results.")
        ] = None,
        per_page: Annotated[
            Optional[int],
            Field(description="Number of results per page to limit response size.")
        ] = None,
):
    endpoint = "/emailer_messages/search"
    params = {}

    # 由于参数名里带[]，httpx params支持传多值字典或tuple
    if emailer_message_stats is not None:
        params["emailer_message_stats[]"] = emailer_message_stats
    if emailer_message_reply_classes is not None:
        params["emailer_message_reply_classes[]"] = emailer_message_reply_classes
    if user_ids is not None:
        params["user_ids[]"] = user_ids
    if email_account_id_and_aliases is not None:
        params["email_account_id_and_aliases"] = email_account_id_and_aliases
    if emailer_campaign_ids is not None:
        params["emailer_campaign_ids[]"] = emailer_campaign_ids
    if not_emailer_campaign_ids is not None:
        params["not_emailer_campaign_ids[]"] = not_emailer_campaign_ids
    if emailer_message_date_range_mode is not None:
        params["emailer_message_date_range_mode"] = emailer_message_date_range_mode
    if emailerMessageDateRange_max is not None:
        params["emailerMessageDateRange[max]"] = emailerMessageDateRange_max
    if emailerMessageDateRange_min is not None:
        params["emailerMessageDateRange[min]"] = emailerMessageDateRange_min
    if not_sent_reason_cds is not None:
        params["not_sent_reason_cds[]"] = not_sent_reason_cds
    if q_keywords is not None:
        params["q_keywords"] = q_keywords
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page

    try:
        result = await apollo_client.make_request(method="GET", endpoint=endpoint, params=params)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Post API usage stats (no parameters).")
async def post_apiusage():
    endpoint = "/usage_stats/api_usage_stats"
    try:
        result = await apollo_client.make_request(method="POST", endpoint=endpoint)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Create a phone call record in Apollo.")
async def phonecalls_create(
        logged: Annotated[
            Optional[bool],
            Field(description="Set to `true` if you want to create an individual record for the phone call in Apollo.")
        ] = None,
        user_id: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Designate the caller in your team's Apollo account. "
                        "Use the Get a List of Users endpoint to retrieve IDs. "
                        "Example: `67e33d527de088000daa60c4`"
                )
            )
        ] = None,
        contact_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Designate the contact that was called. "
                        "Use the Search for Contacts endpoint to retrieve IDs. "
                        "Example: `66e34b81740c50074e3d1bd4`"
                )
            )
        ] = None,
        account_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Associate the call with an account. "
                        "Use the Search for Accounts endpoint to retrieve IDs. "
                        "Example: `66e9abf95ac32901b20d1a0d`"
                )
            )
        ] = None,
        to_number: Annotated[
            Optional[str],
            Field(description="The phone number that you dialed. Example: `5551234567`")
        ] = None,
        from_number: Annotated[
            Optional[str],
            Field(description="The phone number that dialed you. Example: `5551234567`")
        ] = None,
        status: Annotated[
            Optional[str],
            Field(
                description=(
                        "The status of the phone call. Possible values include: "
                        "`queued`, `ringing`, `in-progress`, `completed`, `no_answer`, `failed`, `busy`."
                )
            )
        ] = None,
        start_time: Annotated[
            Optional[str],
            Field(
                description=(
                        "The time when the call started. ISO 8601 date-time format, GMT by default. "
                        "Example: `2025-02-15T08:10:30Z`; `2025-03-25T10:15:30+05:00Z`"
                )
            )
        ] = None,
        end_time: Annotated[
            Optional[str],
            Field(
                description=(
                        "The time when the call ended. ISO 8601 date-time format, GMT by default. "
                        "Example: `2025-05-15T08:10:30Z`; `2025-05-25T10:15:30+05:00Z`"
                )
            )
        ] = None,
        duration: Annotated[
            Optional[int],
            Field(description="The duration of the call in seconds. Examples: `120`; `205`")
        ] = None,
        phone_call_purpose_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Assign a call purpose to the record. Unique to your team's Apollo account. "
                        "Example: `6095a710bd01d100a506d4cd`"
                )
            )
        ] = None,
        phone_call_outcome_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Assign a call outcome to the record. Unique to your team's Apollo account. "
                        "Example: `6095a710bd01d100a506d4c5`"
                )
            )
        ] = None,
        note: Annotated[
            Optional[str],
            Field(
                description="Add a note to the call record. Example: `This lead is interested in learning more about our new product line.`")
        ] = None,
):
    endpoint = "/phone_calls"
    params = {}

    if logged is not None:
        params["logged"] = str(logged).lower()
    if user_id is not None:
        params["user_id[]"] = user_id
    if contact_id is not None:
        params["contact_id"] = contact_id
    if account_id is not None:
        params["account_id"] = account_id
    if to_number is not None:
        params["to_number"] = to_number
    if from_number is not None:
        params["from_number"] = from_number
    if status is not None:
        params["status"] = status
    if start_time is not None:
        params["start_time"] = start_time
    if end_time is not None:
        params["end_time"] = end_time
    if duration is not None:
        params["duration"] = duration
    if phone_call_purpose_id is not None:
        params["phone_call_purpose_id"] = phone_call_purpose_id
    if phone_call_outcome_id is not None:
        params["phone_call_outcome_id"] = phone_call_outcome_id
    if note is not None:
        params["note"] = note

    try:
        result = await apollo_client.make_request(method="POST", endpoint=endpoint, params=params)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Update an existing phone call record in Apollo.")
async def put_phone_callsupdate(
        id: Annotated[
            str,
            Field(
                description=(
                        "The Apollo ID for the call record that you want to update. "
                        "To find call record IDs, call the Search for Calls endpoint and identify the `id` value. "
                        "Example: `6859b0dd828b270021e69648`"
                )
            )
        ],
        logged: Annotated[
            Optional[bool],
            Field(description="Set to `true` if you want to create an individual record for the phone call in Apollo.")
        ] = None,
        user_id: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Designate the caller in your team's Apollo account. "
                        "Use the Get a List of Users endpoint to retrieve IDs. "
                        "Example: `67e33d527de088000daa60c4`"
                )
            )
        ] = None,
        contact_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Designate the contact that was called. "
                        "Use the Search for Contacts endpoint to retrieve IDs. "
                        "Example: `66e34b81740c50074e3d1bd4`"
                )
            )
        ] = None,
        account_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Associate the call with an account. "
                        "Use the Search for Accounts endpoint to retrieve IDs. "
                        "Example: `66e9abf95ac32901b20d1a0d`"
                )
            )
        ] = None,
        to_number: Annotated[
            Optional[str],
            Field(description="The phone number that you dialed. Example: `5551234567`")
        ] = None,
        from_number: Annotated[
            Optional[str],
            Field(description="The phone number that dialed you. Example: `5551234567`")
        ] = None,
        status: Annotated[
            Optional[str],
            Field(
                description=(
                        "The status of the phone call. Possible values include: "
                        "`queued`, `ringing`, `in-progress`, `completed`, `no_answer`, `failed`, `busy`."
                )
            )
        ] = None,
        start_time: Annotated[
            Optional[str],
            Field(
                description=(
                        "The time when the call started. ISO 8601 date-time format, GMT by default. "
                        "Example: `2025-02-15T08:10:30Z`; `2025-03-25T10:15:30+05:00Z`"
                )
            )
        ] = None,
        end_time: Annotated[
            Optional[str],
            Field(
                description=(
                        "The time when the call ended. ISO 8601 date-time format, GMT by default. "
                        "Example: `2025-05-15T08:10:30Z`; `2025-05-25T10:15:30+05:00Z`"
                )
            )
        ] = None,
        duration: Annotated[
            Optional[int],
            Field(description="The duration of the call in seconds. Examples: `120`; `205`")
        ] = None,
        phone_call_purpose_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Assign a call purpose to the record. Unique to your team's Apollo account. "
                        "Example: `6095a710bd01d100a506d4cd`"
                )
            )
        ] = None,
        phone_call_outcome_id: Annotated[
            Optional[str],
            Field(
                description=(
                        "Assign a call outcome to the record. Unique to your team's Apollo account. "
                        "Example: `6095a710bd01d100a506d4c5`"
                )
            )
        ] = None,
        note: Annotated[
            Optional[str],
            Field(
                description="Add a note to the call record. Example: `This lead is interested in learning more about our new product line.`")
        ] = None,
):
    endpoint = f"/phone_calls/{id}"
    params = {}

    if logged is not None:
        params["logged"] = str(logged).lower()
    if user_id is not None:
        params["user_id[]"] = user_id
    if contact_id is not None:
        params["contact_id"] = contact_id
    if account_id is not None:
        params["account_id"] = account_id
    if to_number is not None:
        params["to_number"] = to_number
    if from_number is not None:
        params["from_number"] = from_number
    if status is not None:
        params["status"] = status
    if start_time is not None:
        params["start_time"] = start_time
    if end_time is not None:
        params["end_time"] = end_time
    if duration is not None:
        params["duration"] = duration
    if phone_call_purpose_id is not None:
        params["phone_call_purpose_id"] = phone_call_purpose_id
    if phone_call_outcome_id is not None:
        params["phone_call_outcome_id"] = phone_call_outcome_id
    if note is not None:
        params["note"] = note

    try:
        result = await apollo_client.make_request(method="PUT", endpoint=endpoint, params=params)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool(description="Search news articles related to specific organizations in Apollo.")
async def news_articles_search(
        organization_ids: Annotated[
            List[str],
            Field(
                description=(
                        "The Apollo IDs for the companies you want to include in your search results. "
                        "To find IDs, call the Organization Search endpoint and identify the values for `organization_id`. "
                        "Example: `5e66b6381e05b4008c8331b8`"
                )
            ),
            # 必填，非空数组
        ],
        categories: Annotated[
            Optional[List[str]],
            Field(
                description=(
                        "Filter your search to include only certain categories or sub-categories of news. "
                        "Use the News search filter for companies within Apollo to uncover all possible categories and sub-categories. "
                        "Examples: `hires`; `investment`; `contract`"
                )
            )
        ] = None,
        published_at_min: Annotated[
            Optional[str],
            Field(
                alias="published_at[min]",
                description=(
                        "Set the lower bound of the date range you want to search. Use with `published_at[max]`. "
                        "Date format: `YYYY-MM-DD`. Example: `2025-02-15`"
                ),
                pattern=r"^\d{4}-\d{2}-\d{2}$"
            )
        ] = None,
        published_at_max: Annotated[
            Optional[str],
            Field(
                alias="published_at[max]",
                description=(
                        "Set the upper bound of the date range you want to search. Use with `published_at[min]`. "
                        "Date format: `YYYY-MM-DD`. Example: `2025-05-15`"
                ),
                pattern=r"^\d{4}-\d{2}-\d{2}$"
            )
        ] = None,
        page: Annotated[
            Optional[int],
            Field(
                description=(
                        "The page number of the Apollo data that you want to retrieve. "
                        "Use with `per_page` for pagination. Example: `4`"
                )
            )
        ] = None,
        per_page: Annotated[
            Optional[int],
            Field(
                description=(
                        "The number of search results that should be returned per page. "
                        "Limiting results improves endpoint performance. Example: `10`"
                )
            )
        ] = None,
):
    endpoint = "/news_articles/search"
    params = {}

    # 必填参数 organization_ids 需要带中括号 key 发送
    params["organization_ids[]"] = organization_ids

    if categories is not None:
        params["categories[]"] = categories
    if published_at_min is not None:
        params["published_at[min]"] = published_at_min
    if published_at_max is not None:
        params["published_at[max]"] = published_at_max
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page

    try:
        result = await apollo_client.make_request(method="POST", endpoint=endpoint, params=params)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API request failed: {e.response.status_code} {e.response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def main():
    mcp.run()


if __name__ == '__main__':
    main()
