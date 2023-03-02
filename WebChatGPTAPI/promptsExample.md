# API prompt

Here is my Input you need to Output:
Input: {query}
Instructions:
Your task is to list calls to a Question Answering API to a piece of text. The questions should help you get information for better understand the input and collect some related information. You can call the API by writing "[(API)(question)]" where "question" is the full complete question you want to ask for better answer the input and the question should be as short as possible, and you can turn a large question into smaller ones by call the API more time. 
.The API available is ['WikiSearch','Calculator','Google'],you need to choose one to fill in each of the "[(API)(question)]"
Here are some examples of API calls:
{
Input: Joe Biden was born in Scranton, Pennsylvania.
Output: {"calls": [{"API": "Google", "query": "Where was Joe Biden born?"},]}
Input: Coca-Cola, or Coke, is a carbonated soft drink manufactured by the Coca-Cola Company.
Output: {"calls": [{"API": "Google", "query": "What other name is Coca-Cola known by?"},
{"API": "Google", "query": "Who manufactures Coca-Cola?"}]}
Input: The New England Journal of Medicine is a registered trademark of  the MMS.
Output: {"calls":[{"API": "Google", "query": "Who is the publisher of The New England Journal of Medicine?"}]}
Input: Out of 1400 participants, 400 passed the test.
Output: {"calls":[{"API": "Calculator", "query": "400 / 1400"}]}
Input: The name derives from "la tortuga", the Spanish word for turtle.
Output: {"calls": [{"API": "WikiSearch", "query": "tortuga"}]}
Input: The Brown Act is California's law that requires legislative bodies, like city councils, to hold their meetings open to the public.
Output: {"calls": [{"API": "WikiSearch", "query": "Brown Act"}]}
Input: 孔子是怎么火烧赤壁的?
Output: {"calls":[{"API": "WikiSearch","query": "孔子"},{"API": "WikiSearch","query": "火烧赤壁"}]}
Input: 强化学习中的策略梯度是什么,用通俗语言解释下
Output: {"calls": [{"API": "Google", "query": "强化学习中的策略梯度"}]}
}
Remember: dont't really call the api and output any other text, Just output the API call in JSON type

# Wolfram Alpha prompt

WolframAlpha JSON results:

Desiderio Rodriguez
WolframAlpha JSON results:

{web_results}

Instructions: Using the provided Wolfram Alpha JSON results, write a comprehensive and detailed corect reply to the given query. Using latex to express the whole results.
Query: {query}

# Web Extraction prompt

a WebSite Extraction in JSON type:
{web_results}

Current date: 2/22/2023
Instructions: Using the provided Extract Website results in JSON type, write a comprehensive reply to the given query in a understandable and relatively detailed language. Make sure to cite results using [the counting of sentence] notation after the reference.
WebsitesURL: {query}

# word flash card prompt

Here is the word I give you : "what's the meaning of  English word tout"

Here is the web serach result of the word wraped by big brackets:
{{web_results}}

I need you to act as a anki helper for my English study for TOEFL exam, I've already give you the word and its search results. You need to help me memorize the words by offer some format of anki card which likes the 'front-back' form by using the codeblocks to enwrap the Front and Back part serparately, and combine some related information from the web result to the back of the anki card to better illustrate it.

First, in the back of the card you need to illustrate this word in a easy-understanding and consice way whose word limitation is 64 words and maxium 4 different meanings, each meanings should less thant 16 words and give each meaning a setence example as its sublist.
Second, list some synoms of it, which at least 5. 
Third, list some deriatives of it, which at least 5. 
And The back of the card content need to be the format of lists. 
Fourth, give an imagiable vivid scene of the word to help me memorize, which is less than 16 words.
Here is an example wraped by big brackets to help you better understanding:
{
Front:

```markdown
forge
/fôrj/
```

Back:

```markdown
# Meanings:
- verb
    - make or shape (a metal object) by heating it in a fire or furnace and beating or hammering it.
        - "he forged a great suit of black armor"
    - create (a relationship or new conditions).
        - "the two women forged a close bond"
- noun
    - a blacksmith's workshop; a smithy.
        - "Tom is learning some skills in his Dad's forge"

# Synonyms:
create, shape, establish, strengthen, counterfeit, imitate.

# Deriatives:
unforgettable, reforge, unforgettably, unforgeable, unforgeability

# Image:
a blacksmith is forge in his workshop.
```

}
Remember, dont't output other unrelated information,just output the card,and output it more understandable and consice way