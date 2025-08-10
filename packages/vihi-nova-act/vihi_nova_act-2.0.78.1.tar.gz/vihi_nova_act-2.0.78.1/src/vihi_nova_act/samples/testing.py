from vihi_nova_act import NovaAct

with NovaAct(starting_page="https://www.amazon.com", stream=True, preview={"playwright_actuation": True},) as nova:
    gen = nova.act("search for a coffee maker")

    while True:
        try:
            line = next(gen)
            # print(line)
            # observations.append(line.get("observation"))
            # agent_thinkings.append(line.get("agent_thinking"))
            # tool_calls.append(line.get("tool_call"))

            print(
                f"Observations:{line.get('observation')}"
            )
            print(
                f"Agent thinking:{line.get('agent_thinking')}"
            )
            print(f"Tool call:{line.get('tool_call')}")
        except StopIteration as e:
            final_return_value = e.value  # catch the return value here
            print(f"final_return_value: {final_return_value}")
            break
    # nova.act("select the first result")
    # nova.act("scroll down or up until you see 'add to cart' and then click 'add to cart'")