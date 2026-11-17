# Eval results (tfidf retrieval, top_k=4, 20 questions)

- Retrieval hit@4 (correct lecture in top results): **18/18**
- Context recall (expected facts present in retrieved text): **81%**

Model: `claude-haiku-5-5`

| Prompt variant | Answer accuracy | Correct refusals | Avg latency (s) |
|---|---|---|---|
| basic | 81% | 0/2 | 2.59 |
| grounded | 81% | 2/2 | 1.98 |
| grounded_cited | 76% | 2/2 | 2.15 |

## Missed questions per variant
**basic**
- What is the net present value of project 1 at a 10% discount rate? (score 0%)
- Which project has the highest NPV and which is not worth considering? (score 0%)
- What is Step 0 in Step Wise project planning? (score 50%)
- What are the advantages of off-the-shelf software? (score 50%)
- What are the disadvantages of off-the-shelf software? (score 50%)
- What is the syntax of a Kubernetes Deployment YAML file? (should have refused)
- Who won the 2022 FIFA World Cup? (should have refused)

**grounded**
- What is the definition of a project in the basic definitions? (score 0%)
- What is the net present value of project 1 at a 10% discount rate? (score 0%)
- Which project has the highest NPV and which is not worth considering? (score 0%)
- What is Step 0 in Step Wise project planning? (score 50%)

**grounded_cited**
- What is the definition of a project in the basic definitions? (score 0%)
- Why are software projects different from other projects? (score 25%)
- What is the net present value of project 1 at a 10% discount rate? (score 0%)
- Which project has the highest NPV and which is not worth considering? (score 0%)
- What is Step 0 in Step Wise project planning? (score 50%)
