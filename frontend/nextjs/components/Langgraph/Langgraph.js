import { Client } from "@langchain/langgraph-sdk";
import { task } from '../../config/task';

export async function startLanggraphResearch(newQuestion, report_source, langgraphHostUrl) {
    // If using local backend, use HTTP API instead of LangGraph Cloud
    if (langgraphHostUrl && langgraphHostUrl.includes('gptr-gpt-researcher')) {
        console.log('🏠 Using local backend HTTP API for multi-agents research');
        
        const response = await fetch(`${langgraphHostUrl}/api/multi_agents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: newQuestion,
                report_source: report_source
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Create a mock stream response for compatibility
        const mockStreamResponse = {
            async *[Symbol.asyncIterator]() {
                const reader = response.body?.getReader();
                if (!reader) return;
                
                const decoder = new TextDecoder();
                let done = false;
                
                while (!done) {
                    const { value, done: doneReading } = await reader.read();
                    done = doneReading;
                    
                    if (value) {
                        const chunk = decoder.decode(value);
                        yield { data: { report: chunk, type: 'report' } };
                    }
                }
            }
        };

        return {
            streamResponse: mockStreamResponse,
            host: langgraphHostUrl,
            thread_id: 'local-' + Date.now()
        };
    }

    // Original LangGraph Cloud code
    // Update the task query with the new question
    task.task.query = newQuestion;
    task.task.source = report_source;
    const host = langgraphHostUrl;
    
    // Add your Langgraph Cloud Authentication token here
    const authToken = '';

    const client = new Client({
        apiUrl: host,
        defaultHeaders: {
            'Content-Type': 'application/json',
            'X-Api-Key': authToken
        }
    });
  
    // List all assistants
    const assistants = await client.assistants.search({
      metadata: null,
      offset: 0,
      limit: 10,
    });
  
    console.log('assistants: ', assistants);
  
    // We auto-create an assistant for each graph you register in config.
    const agent = assistants[0];
  
    // Start a new thread
    const thread = await client.threads.create();
  
    // Start a streaming run
    const input = task;
  
    const streamResponse = client.runs.stream(
      thread["thread_id"],
      agent["assistant_id"],
      {
        input,
      },
    );

    return {streamResponse, host, thread_id: thread["thread_id"]};
}
