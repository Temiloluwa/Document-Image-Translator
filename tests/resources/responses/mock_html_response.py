from google.genai.types import (
    GenerateContentResponse,
    Candidate,
    Content,
    Part,
    GenerateContentResponseUsageMetadata,
    ModalityTokenCount,
    FinishReason,
    MediaModality,
)

mock_html_response = GenerateContentResponse(
    candidates=[
        Candidate(
            content=Content(
                parts=[
                    Part(
                        text="""
<html>
<head><title>EUROZONE</title></head>
<body>
<h1>EUROZONE</h1>
<p>19 countries, one currency: <b>Eurozone</b> is the unofficial name for the 19 EU states that are members of the European Economic and Monetary Union (EMU) and have introduced the Euro as a common means of payment. The EMU started in 1999 with eleven states, the others joined over the years. Euro banknotes and coins were put into circulation in 2002, replacing national currencies as legal tender. The seat of the European Central Bank (ECB) is Frankfurt am Main. The President of the ECB since November 1, 2019 is the Frenchwoman Christine Lagarde.</p>
<h2>Facts &amp; Figures</h2>
<p>The EU is a unique construct in the world: It is an association of democratic European states that have set the preservation of peace and the pursuit of prosperity as their highest goals.</p>
<h2>NEW MEMBERS</h2>
<p>Two countries that have chances of joining the EU are Albania and North Macedonia. Only recently, the member states agreed to the proposal of the EU Commission to start accession talks with the two Western Balkan states. "Their future lies in the EU," says EU Enlargement Commissioner Olivér Várhelyi. The EU Commission has long been strongly advocating for enlargement in the Western Balkans.</p>
<h3>POPULATION</h3>
<h2>SIGNIFICANT DIFFERENCES</h2>
<p>Around 447 million people live in the 27 member states of the EU - after India and China, this is the world's third largest population. With 85.1 million inhabitants, Germany is the most populous member state, ahead of France (67 million), Italy (60.4 million), Spain (46.9 million), and Poland (57.9 million). With the withdrawal of Great Britain at the end of January 2020, the EU lost around 66.6 million inhabitants. The area of the community of states is more than four million km². In terms of area, France is the largest and Malta is the smallest country in the EU. With 557.576 km², Germany is the fourth largest EU state in terms of area.</p>
<!-- Example image tag for embedding -->
<img id="img-0" src="img-0.jpeg" alt="Eurozone map" />
</body>
</html>
"""
                    )
                ],
                role="model",
            ),
            citation_metadata=None,
            finish_message=None,
            token_count=None,
            finish_reason=FinishReason.STOP,
            avg_logprobs=None,
            grounding_metadata=None,
            index=0,
            logprobs_result=None,
            safety_ratings=None,
        )
    ],
    create_time=None,
    response_id=None,
    model_version="models/gemini-2.5-flash-preview-04-17",
    prompt_feedback=None,
    usage_metadata=GenerateContentResponseUsageMetadata(
        cache_tokens_details=None,
        cached_content_token_count=None,
        candidates_token_count=442,
        candidates_tokens_details=None,
        prompt_token_count=664,
        prompt_tokens_details=[
            ModalityTokenCount(modality=MediaModality.TEXT, token_count=664)
        ],
        thoughts_token_count=1721,
        tool_use_prompt_token_count=None,
        tool_use_prompt_tokens_details=None,
        total_token_count=2827,
        traffic_type=None,
    ),
    automatic_function_calling_history=[],
    parsed=None,
)
