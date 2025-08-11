import json
import os
from pogodoc import PogodocClient, RenderConfig, UpdateTemplateRequestTemplateInfo, SaveCreatedTemplateRequestTemplateInfo, InitializeRenderJobRequestFormatOpts
from dotenv import load_dotenv

load_dotenv()

def readJson(path: str):
    with open(path, "r") as f:
        return json.load(f)
    
sampleData = readJson("../../data/json_data/react.json")
templatePath = "../../data/templates/React-Demo-App.zip"

def main():
    client = PogodocClient(token=os.getenv("POGODOC_API_TOKEN"))

    test_readme_example()

    test_document_generations(client)

    # save template
    templateId = client.save_template(
        path=templatePath, 
        template_info=SaveCreatedTemplateRequestTemplateInfo(
            title="Test Template",
            description="Test Description", 
            type="html",
            sample_data=sampleData, 
            categories=["invoice"]
        )
    )

    # generate document
    document = client.generate_document(template_id=templateId, data=sampleData, render_config=RenderConfig(type="html", target="pdf"))
    print(document)

    # get template index html
    templateHtml = client.templates.get_template_index_html(template_id=templateId)
    print(templateHtml)

    # update template
    contentId = client.update_template(template_id=templateId, path=templatePath, template_info=UpdateTemplateRequestTemplateInfo(title="Test Template", description="Test Description", type="html", sample_data=sampleData, categories=["invoice"]))
    print(contentId)

    # generate presigned url
    presignedUrl = client.templates.generate_presigned_get_url(template_id=templateId)
    print(presignedUrl)

    # immediate render with template string
    immediateRender = client.documents.start_immediate_render(template="<h1>Hello <%= name %></h1>", data={"name": "John Doe"}, target="pdf", type="html")
    print(immediateRender)

    # # delete template
    # client.templates.delete_template(template_id=templateId)

def test_readme_example():
    client = PogodocClient(
        token=os.getenv("POGODOC_API_TOKEN"),
    )

    response = client.generate_document(
        template_id = os.getenv("TEMPLATE_ID"),
        data = {"name": "John Doe"},
        render_config = RenderConfig(
            type = "html",
            target = "pdf",
            format_opts = InitializeRenderJobRequestFormatOpts(
                from_page = 1,
            ),
        ),
    )

    print("README Generated document url:\n", response.output.data.url)

def test_document_generations(client: PogodocClient):
    template_id = os.getenv("TEMPLATE_ID")

    sampleData = {
        "name": "John Doe",
    }

    # immediate document generation
    immediate_document = client.generate_document_immediate(template_id=template_id, data=sampleData, render_config=RenderConfig(type="html", target="pdf"))
    print("immediateDocument:", immediate_document)
    
    # document generation
    document = client.generate_document(data=sampleData, render_config=RenderConfig(type="html", target="pdf"), template_id=template_id)
    print("document:", document)

    # start document generation
    job_id = client.start_generate_document(data=sampleData, render_config=RenderConfig(type="html", target="pdf"), template_id=template_id)
    print("startDocument:", job_id)

    # poll for job completion
    job_status = client.poll_for_job_completion(job_id)
    print("jobStatus:", job_status)
    

if __name__ == "__main__":
    main()

    
