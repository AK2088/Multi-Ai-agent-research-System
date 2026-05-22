from agent import build_reader_agent,build_search_agent,writer_chain,critic_chain

def run_research_pipeline(topic: str) -> dict:
    state={}

    # search agent wotking
    print("\n"+" ="*50)
    print("step 1 - search agent is working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result =search_agent.invoke({ 
        "messages": [("user", f"Find recent, relaible and detailed information about: {topic}")]
    })

    state["search_results"] = search_result["messages"][-1].content

    print("\n Search result ", state["search_results"])

    # step 2- reader agent

    print("\n"+" ="*50)
    print("step 2 - reader agent is scraping top resources...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content']=reader_result['messages'][-1].content

    print("\n Screaped Content",state["scraped_content"])


    # step 3 - writer chain\
    print("\n"+" ="*50)
    print("step 3 - Writer is drafting a report...")
    print("="*50)

    research_combines = (
        f"Search results : \n{state['search_results']}\n\n"
        f"Detailed Screaped content : \n {state['scraped_content']}" 
    )   

    state['report']= writer_chain.invoke({
        "topic": topic,
        "research": research_combines,
    }) 

    print("\n Final report \n ",state["report"])


    #step 4- critic report
    print("\n"+" ="*50)
    print("step 4 - Critic is reviewing the report")
    print("="*50)

    state['feedback']=critic_chain.invoke({
        "report": state['report'],
    })

    print("\n Critc Report\n",state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a Research Topic :")
    run_research_pipeline(topic)


