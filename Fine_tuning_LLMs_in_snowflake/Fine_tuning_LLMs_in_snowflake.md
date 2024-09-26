# Fine-tuning LLMs in Snowflake

![Machine Learning](./images/machine_learning.png)

**TL;DR:**
Cortex Fine-tuning is a fully managed service that lets you fine-tune popular LLMs using your data, all within Snowflake.

[A large language model (LLM)](https://en.wikipedia.org/wiki/Large_language_model) is an AI Model that *understands* natural language and generates a text as a response.

Fine-tuning means modifying/customizing something to better suit your needs. Snowflake has a function called Cortex Fine-tuning that allows you to further tain large language models (called base models) to better suit a specific task.

**To super oversimplify** what LLMs are and how they work, LLM is a collection of  algorithms that while training learn correlation between words. LLMs are trained on lots of data. After training, LLMs respond to your questions based on what they have seen in their training data and correlation between words.
LLMs compose their answer one word at a time, every time they try to add a new word to their answer, they calculate the probability of what word might come after the current sequence of words in the answer.
For example, let's say the LLM is forming an answer to your question, "What is something that nowadays everyone owns". It has formed a beginning of a sentence "Nowadays everyone seems to own ..", to finish the sentence it checks the common words that it had usually seen with the words "nowadays", "everyone", "owns" in its training data. based on its training data, the common words that might come after "nowadays", "everyone", "owns" are "a smartphone" with probability of 80%, "a car" with the probability of 60%, "a house" with the probability of 5%. Since the smartphone has the highest probability, LLM chooses Smartphone ans answers "Nowadays everyone seems to own a smartphone".

**Imagine** this LLM was trained on only data that was available up until 1900s, meaning it has no idea about smartphone or even cars.
In that case, this the same LLM would answer to the same question of  "What is something that nowadays everyone owns?" as "Nowadays everyone seems to own a wood stove". Because on its training data it had seen "wood stove" being used with other words "everyone", "owns" etc. so it associated the "wood stove" with above words.
Or if the LLM had a limited data during its training about (Microsoft) Windows and Apple (a company), it might associate these words with a physical structure and a fruit rather than an operating system and a tech company.

Snowflake docs state:
> If you don’t want the high cost of training a large model from scratch but need better latency and results than you’re getting from prompt engineering or even retrieval augmented generation (RAG) methods, fine-tuning an existing large model is an option.

What it means is that

1. developing a large language model is very expensive and takes a lot of time & expertise
1. the LLMs available for use (open-source, commercial etc.) may not suit your needs completely, i.e LLMs may not be trained enough on a certain domain specific fields.
    Most likely these LLMs are not trained on your private data (that belong to you company), so while answering your questions, they answer based on public data not your internal data.

As a middle ground, you can use these LLMs as a base model and further train/customize them to fit your needs better.

> Fine-tuning allows you to use *examples* to adjust the behavior of the model and improve the model’s knowledge of domain-specific tasks.

Snowflake doesn't reveal much of inner workings of fine-tuning process.

**How you fine-tune a model in Snowflake is by providing example prompts and answers.**

**Note:** If Snowflake decided to remove a base model from its platform for whatever reason, your fine-tuned model will no longer work.

## Models available to fine-tune

- `mistral-7b` by Mistral AI
- `mixtral-8x7b` by Mistral AI
- `llama3-8b` by Meta
- `llama3-70b` by Meta

`b` is the the number of parameters used in training these models.
The number of parameters typically correlates with the model's capacity to learn complex patterns. A model with more parameters can often capture more intricate relationships in data, leading to better performance on various tasks. But higher number of parameters also influence resource utilization.

The main takeaway here is a model with higher number of parameters usually performs better and requires more computational power to run.

## Fine Tuning the base model

You can fine tune a base model in snowflake by choosing a base model and feeding it prompt and response pairs.

You should have a table or view that must have one column consisting of prompts and another column consisting of answers to those prompts.
Ideally the column names should be "prompt" and "completion", but if it is not the case, you can use aliases.
**Note:** Table or view can have more than two columns, but to fine-tune a model only two columns will be used.

Snowflake provides [SNOWFLAKE.CORTEX.FINETUNE](https://docs.snowflake.com/en/sql-reference/functions/finetune-snowflake-cortex) function for fine-tuning models.

Fine-tuning a model is a time-consuming process. You start/create the process and snowflake runs it until its completion. After creating the fine-tuning process you can close your browser/tab etc.

Example:

```sql
SELECT SNOWFLAKE.CORTEX.FINETUNE(
  'CREATE',
  'my_super_llama',
  'llama3-8b',
  'SELECT question AS prompt, answer AS completion FROM training_dataset',
  'SELECT prompt, response AS completion FROM validation_dataset'
);
```

Above command returns the ID of the fine-tuning process.

You can get the list of the fine-tuning processes via `SNOWFLAKE.CORTEX.FINETUNE('SHOW')` command.
If you want to check status of a specific fine-tuning process, you can use `SNOWFLAKE.CORTEX.FINETUNE('DESCRIBE', '<finetune_job_id>')` command.

If you change your mind, and want to abort fine-tuning process you can use `SNOWFLAKE.CORTEX.FINETUNE('CANCEL', '<finetune_job_id>')` command to cancel the process.

**Keep in mind** there is context window limitation. Context window is a number of tokens an LLM can process at a time. In simple terms, it is the length of the text an LLM can process.

Below is the breakdown of the context window for each base model:

|Model|Context Window|Input Context (prompt)|Output Context (completion)|
|---|---|---|---|
|mistral-7b |32k |28k |4k|
|llama3-8b|8k|6k|2k|
|mixtral-8x7b |32k |28k |4k|
|llama3-70b|8k|6k|2k|

## Using Fine-tuned model

After successful fine-tuning of the base model, you can use it similar to any other LLM on snowflake via [SNOWFLAKE.CORTEX.COMPLETE](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-finetuning) function.

Syntax:

```SQL
SNOWFLAKE.CORTEX.COMPLETE(
    <model_name>, <prompt_or_history> [ , <options> ] )
```

Example:

```SQL
SELECT SNOWFLAKE.CORTEX.COMPLETE('my_super_llama',
    'What is the core principle of our ABC company?');
```

## Necessary Privileges

- `USAGE` on the database that the training (and validation) data are queried from.

- `OWNERSHIP` or (`CREATE MODEL` and `USAGE`) on the schema that the model is saved to.

- `SNOWFLAKE.CORTEX_USER` on the database that the model is saved to.

## Cost

The Snowflake Cortex Fine-tuning function incurs compute cost based on the number of tokens used in training.

*A token is the smallest unit of text processed by the Snowflake Cortex Fine-tuning function, approximately equal to four characters of text.*

There are also storage and warehouse (compute) costs for storing data, and for running any SQL commands.

---

## Fine-tuning vs RAG

The purpose of Fine-tuning is to improve LLM's response accuracy.
There is another method too to achieve the same goal called Retrieval Augmented Generation (RAG).
RAG is an LLM optimization method introduced by Meta in 2020.

So what is the difference between the two in simple words?
Fine-tuning is retraining the base model on a specific domain. We can think of it making a base model smarter with regard to specific domain such as medicine, or philosophy by enabling it to discover patterns/associations in a more specific field.

RAG is providing relevant information to a LLM with prompting it.
When user submits a prompt to a LLM that has RAG, the process unfolds in the following way:

1. **R**etrieval of relevant information from database or internet based on the set-up.
1. Retrieved information is added (**A**ugmented) to the user's query and submitted to the LLM as a prompt.
1. LLM **G**enerates response using user's query and Retrieved information.

We can think of it as giving a medical book to a fairly smart person and asking them to answer our questions using the book & their general knowledge.

RAG optimization requires complex set-up and it is more resource intensive to run since this set-up requires querying the database every time. Also since the retrieved information is added to user's query as a prompt to LLM, context-window limitation might be an issue.

As for fine-tuning, it is similar to training the person in a specified field. Using above example, it would be making the fairly smart person go to medical school to study and after they graduate asking them to answer our questions using their **learnt** knowledge.

Fine-tuning a base model requires lots of compute resources but once training is finished, running fine-tuned LLM is less resource intensive than running RAG LLM.

Generally speaking, RAG LLM produces more accurate answers.
Another advantage is that if the RAG LLM is hooked up to internet or frequently updated Database, this set-up produces more up-to-date answers, while fine-tuned LLM answers solely based on the data it has seen during its training.

The best thing is these two optimization methods can be used together, making the base model smarter and providing it with (up-to-date) relevant information.

You can learn more about differences between fine-tuning and RAG in below articles:

- [RAG vs. fine-tuning](https://www.ibm.com/think/topics/rag-vs-fine-tuning) by Ivan Belcic and Cole Stryker, IBM
- [RAG vs. fine-tuning: Choosing the right method for your LLM](https://www.superannotate.com/blog/rag-vs-fine-tuning) by Superannotate.com

If you want to know how to set-up and use RAG LLM on Snowflake, you can find more information on the [this page](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview).
