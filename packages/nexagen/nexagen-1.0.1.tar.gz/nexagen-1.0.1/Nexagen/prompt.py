generate_agent_cards_prompt="""# Objective
Extract all MCP agents from the provided `mcp_cards.json` and transform them into the Nexagen standard agent cards format. Return the result as a JSON array.

# Input Format
The input JSON, `mcp_cards.json`, contains various charts with tools defined under each chart. Each tool has a name, description, and input schema.

# Output Format
The output should be a JSON array where each object represents an agent card in the Nexagen standard format. Each agent card should include the following fields:
- `name`: Name of the chart.
- `description`: General description of the agent's purpose.
- `url`: Leave this empty or set a default placeholder (e.g., "http://localhost:0000/").
- `version`: Default to "1.0.0".
- `capabilities`: Set default values (e.g., streaming, pushNotifications, stateTransitionHistory).
- `defaultInputModes`: Default to ["text", "text/plain"].
- `defaultOutputModes`: Default to ["text", "text/plain"].
- `skills`: A list of skills where each tool corresponds to a skill with:
  - `id`: Tool name.
  - `name`: Tool name.
  - `description`: Tool description.
  - `tags`: Default to an empty array or based on tool name.
  - `examples`: Default to an empty array.
**Do not return anything other than JSON.**

# Example Output
```json
[
  {
    "name": "Chart Agent",
    "description": "Handles chart-related operations",
    "url": "http://localhost:0000/",
    "version": "1.0.0",
    "capabilities": {
      "streaming": false,
      "pushNotifications": false,
      "stateTransitionHistory": false
    },
    "defaultInputModes": [
      "text",
      "text/plain"
    ],
    "defaultOutputModes": [
      "text",
      "text/plain"
    ],
    "skills": [
      {
        "id": "draw_chart",
        "name": "draw_chart",
        "description": "Generates a chart based on input data array and returns the file path",
        "tags": ["chart", "draw"],
        "examples": []
      }
    ]
  }
]
Instructions
Parse the mcp_cards.json to identify each tool under every chart.
For each chart, create an agent card object with the specified fields.
Map each tool to a skill within the agent card.
Use placeholders for fields not directly available in the MCP format.
Return the final output as a JSON array.
Constraints
Ensure the output JSON is correctly formatted.
Assume default values for unspecified fields in the MCP format.

This prompt ensures that MCP tools are correctly mapped to the skills in the Nexagen format.

#mcp_cards.json content
"""

