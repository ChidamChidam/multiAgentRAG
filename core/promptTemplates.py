#prompts={}

def routerPrompt():
   prompt="""
      You are an intelligent routing agent for a multi-agent AI system.
      Read the user input question carefully and interpret the core task. Follow these rules:

      Question : {input}

      1. Categorize the question as either an analysis or comparison task.
      2. Identify the core subject or theme, giving priority to the main idea or focus
      3. Identify the Key-Element that is in focus of analysis or comparison, like character, plot, tools, techniques, or devices.
      3. If you cannot decide, output 'unknown.'
      Your output should be one of the following 3 formats:

      analyze,<Identified subject>,<Identified Key-Element>
      compare,<Identified subject>,<Identified Key-Element>
      unknown

      Note: The identified subject should be based on the main idea or keyword of the question, even if additional details are present.

      Do not attempt to answer questions outside of these rules.
      """
   return prompt

def ragAnalyzerPrompt():
   prompt="""Analyze the context and along with the title of the context, provide a condensed response in 3 short lines in view of the question below
      {context}
      Question: {question}
      """
   return prompt

def ragComparerPrompt():
   prompt="""compare the 2 stories in the context in view of the question provided
      {context}
      Question: {question}
      
      Respond only with top 3 difference, strictly in a table format
      """
   return prompt