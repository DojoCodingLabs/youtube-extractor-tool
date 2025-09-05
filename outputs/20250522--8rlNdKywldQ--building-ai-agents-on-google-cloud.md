---
type: "video-notes"
source: "youtube"
url: "https://www.youtube.com/watch?v=8rlNdKywldQ"
video_id: "8rlNdKywldQ"
title: "Building AI agents on Google Cloud"
channel: "Google Cloud Tech"
published: "20250522"
created: "2025-09-05 11:37"
tags: ["pr_pr: Google I/O;", "ct:Event - Technical Session;", "ct:Stack - Cloud;"]
---

# Building AI agents on Google Cloud
- Channel: Google Cloud Tech
- Published: 2025-05-22
- Duration: 26 minutes and 24 seconds
- URL: [Watch here](https://www.youtube.com/watch?v=8rlNdKywldQ)

## Executive Summary
In this insightful video, Taran and Vita from Google Cloud delve into the intricacies of building AI agents using Google Cloud technologies, with a particular focus on Cloud Run and Vert.x AI. They provide a detailed exploration of the architecture behind AI agents, emphasizing their capabilities and the potential for enhancing user interactions while automating complex tasks. The presenters underscore the significance of integrating large language models (LLMs) with diverse tools and data sources, enabling the creation of dynamic and adaptable agents capable of performing a wide array of functions, from customer support to data retrieval, all while ensuring reliability and efficiency.

The discussion highlights the evolving paradigm of application architecture driven by AI agents, which leverage both short and long-term memory to plan and execute tasks by breaking them down into manageable components. This flexibility allows AI agents to operate in both synchronous and asynchronous modes, fostering a more interactive user experience. The video concludes by reiterating the essential components for building impactful AI agents, including flexible models, secure tool access, a robust development framework, and interoperability protocols that facilitate collaboration among agents.

## Key Insights

### New Paradigm in Application Architecture
AI agents signify a transformative shift in application architecture, harnessing the power of large language models (LLMs) to execute complex tasks through orchestration. These agents utilize both short and long-term memory, enabling them to decompose tasks into smaller, manageable components. This design allows for operation in synchronous and asynchronous modes, enhancing user interaction. For example, during a code review, an AI agent can engage with the user to clarify requirements, ensuring that the output aligns with user expectations while maintaining a 'human in the loop' approach.

### Enhanced Functionality through Tool Integration
The architecture of AI agents is crafted to integrate various tools and data sources, significantly enhancing their functionality. While LLMs are powerful, they have limitations in areas such as mathematical calculations and real-time data access. AI agents can address these challenges by retrieving context from databases, interacting with APIs, and executing code in secure environments. This multi-tool approach allows agents to deliver more accurate and relevant responses, ultimately improving user satisfaction and operational efficiency.

### Cloud Run: Ideal Deployment Platform
Cloud Run is presented as an optimal platform for deploying AI agents, thanks to its scalability, cost-effectiveness, and user-friendly nature. Operating on a pay-per-use model, it eliminates the need for pre-provisioning capacity, which is particularly advantageous for applications with variable workloads. Developers appreciate the seamless integration with Google Cloud services, enabling rapid and secure deployment of AI agents. The built-in credentials for accessing the Gemini API without manual API key management further streamline the development process, allowing developers to focus on functionality rather than infrastructure management.

### Langraph Framework for Dynamic Agents
The Langraph framework is introduced as a solution for creating dynamic AI agents that blend the reliability of structured workflows with the flexibility of agent-based systems. By modeling control flow as a graph, developers can define decision points and transitions, allowing agents to adapt to varying contexts while maintaining predictability. This approach mitigates risks associated with purely dynamic agents, which can become unreliable if LLMs misinterpret instructions or lack access to appropriate tools.

### Tool Calling for Enhanced Capabilities
Tool calling is a pivotal feature that enhances AI agents' capabilities by allowing LLMs to access external tools as needed. Rather than executing tasks in a fixed sequence, agents can dynamically determine which tools to utilize based on the specific task at hand. This flexibility enables agents to manage complex scenarios more effectively, though it introduces challenges related to reliability. Developers must ensure that tools are well-defined and that agents receive clear instructions to minimize execution errors.

### Vert.x AI: Comprehensive Development Platform
Vert.x AI offers a robust platform for building and managing AI agents, featuring an agent development kit (ADK) that simplifies the development process. The ADK is designed to make agent development resemble traditional software development, complete with built-in tools for debugging and testing. This user-friendly approach empowers developers to create sophisticated agents capable of handling diverse interactions, including text, audio, and video, without requiring extensive coding.

### Interoperability through A2A Protocol
The interoperability of AI agents is highlighted through the introduction of the agent-to-agent (A2A) protocol, which facilitates communication between different agents regardless of their origin. This open standard allows agents to collaborate effectively, sharing capabilities and coordinating actions for complex tasks. For instance, a financial trading agent can work alongside a compliance assessment agent, streamlining workflows. The A2A protocol is designed with enterprise-grade security, ensuring that sensitive information is exchanged securely.

## Frameworks & Methods

### Langraph Control Flow Framework
The Langraph framework is designed for building AI agents that combine the reliability of structured workflows with the flexibility of dynamic agents.
**Steps:**
1. Define the overall task and identify the key decision points that the agent will need to navigate.
2. Model these decision points as nodes in a graph, where each node represents a specific action or tool call.
3. Establish edges between nodes to define the logic and flow of the application, allowing for dynamic transitions based on the agent's reasoning.
4. Implement the agent using the Langraph framework, ensuring that it can access necessary tools and data sources as defined in the control flow.
5. Test the agent to ensure that it can handle various scenarios effectively, adjusting the graph as needed to improve reliability.
**Reference:** [t=40:15]

### Agent Development Kit (ADK)
The ADK is a toolkit for building, deploying, and managing AI agents with a focus on enhancing the developer experience.
**Steps:**
1. Set up the ADK environment by installing the necessary packages and dependencies.
2. Create a new agent project using the ADK command line interface, which initializes the project structure.
3. Develop the agent's functionality by defining its interactions, including tool calls and data processing logic.
4. Utilize the built-in UI for testing and debugging the agent in real-time, allowing for quick iterations and improvements.
5. Deploy the agent to the desired environment, such as Cloud Run or Vert.x AI, ensuring that it is configured for scalability and security.
**Reference:** [t=55:30]

## Key Timestamps
- **[t=02:15]** Introduction to AI agents and their architecture.
- **[t=15:40]** Overview of Cloud Run and its benefits for deploying AI agents.
- **[t=30:10]** Demonstration of building an AI agent using Langraph.
- **[t=42:00]** Introduction to Vert.x AI and its capabilities for agent development.
- **[t=58:20]** Explanation of the agent-to-agent (A2A) protocol for interoperability.
