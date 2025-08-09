from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Creative Frameworks Documentation MCP Server."""
    import os

    doc_sources = [
        {"name": "CreativeOrientation", "llms_txt": os.path.join(os.path.dirname(__file__), "creative_frameworks", "llms-creative-orientation.txt")},
        {"name": "NarrativeRemixing", "llms_txt": os.path.join(os.path.dirname(__file__), "creative_frameworks", "llms-narrative-remixing.txt")},
        {"name": "NonCreativeOrientationApproach", "llms_txt": os.path.join(os.path.dirname(__file__), "creative_frameworks", "llms-non-creative-orientation-approach-to-convert.txt")},
        {"name": "RISEFramework", "llms_txt": os.path.join(os.path.dirname(__file__), "creative_frameworks", "llms-rise-framework.txt")}
    ]
    
    print(SPLASH)
    print("Loading Creative Frameworks documentation...")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()