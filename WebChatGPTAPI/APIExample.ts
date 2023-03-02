//Word Search API
async function WordSearch(query, numResults, timePeriod, region) {
    const headers = new Headers({
        Origin: "https://chat.openai.com",
        "X-RapidAPI-Key": "YOUR_KEY",
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com", "Content-Type": "application/json",
    });
    const url = `https://wordsapiv1.p.rapidapi.com/words/${query}`;
    const response = await fetch(url, { method: "GET", headers, });
    const results = await response.json(); console.log(results); return results;
}

//Google Entity Search API
async function GoogleEntitySearch(query, numResults, timePeriod, region) {
    const headers = new Headers({ Origin: "https://chat.openai.com", });
    const searchParams = new URLSearchParams();
    searchParams.set('query', query);
    searchParams.set('key', 'YOUR_KEY');
    searchParams.set('indent', 'true');
    searchParams.set('limit', numResults.toString());
    const url = `https://kgsearch.googleapis.com/v1/entities:search?${searchParams.toString()}`;
    console.log(url);
    const response = await fetch(url, { method: "GET", headers, });
    const results = await response.json(); console.log(results); return results;
}

//Google search API
async function GoogleSearch(query, numResults, timePeriod, region) {
    const headers = new Headers({ Origin: "https://chat.openai.com", });
    const searchParams = new URLSearchParams();
    searchParams.set('q', query);
    searchParams.set('key', 'YOUR_KEY');
    searchParams.set('cx', 'YOUR_GOOGLE_CLIENT_ID');
    searchParams.set('c2coff', '0');
    searchParams.set('num', numResults.toString());
    const url = `https://customsearch.googleapis.com/customsearch/v1?${searchParams.toString()}`;
    console.log(url);
    const response = await fetch(url, { method: "GET", headers, });
    const results = await response.json();
    const items = results.items;
    const filteredData = items.map(({ title, link, snippet }) => ({
        title,
        link,
        snippet
    }));
    return filteredData;
}
//Google search summarazation API
async function GoogleSearchSimply(query, numResults, timePeriod, region) {
    const headers = new Headers({ Origin: "https://chat.openai.com", });
    const searchParams = new URLSearchParams();
    searchParams.set('q', query);
    searchParams.set('key', 'YOUR_KEY');
    searchParams.set('cx', 'YOUR_GOOGLE_CLIENT_ID');
    searchParams.set('c2coff', '0');
    searchParams.set('num', numResults.toString());
    const url = `https://customsearch.googleapis.com/customsearch/v1?${searchParams.toString()}`;
    console.log(url);
    const response = await fetch(url, { method: "GET", headers, });
    const results = await response.json();
    const items = results.items;
    const filteredData = items.map(({ title, link, snippet }) => ({
        title,
        snippet
    }));
    return filteredData;
}

//summarization arcticle API
async function ArcticleSummarazation(query, numResults, timePeriod, region) {
    const options = {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            'X-RapidAPI-Key': 'YOUR_KEY',
            'X-RapidAPI-Host': 'tldrthis.p.rapidapi.com'
        },
        body: `{"url":"${query}","min_length":250,"max_length":300,"is_detailed":false}`
    };
    const response = await fetch('https://tldrthis.p.rapidapi.com/v1/model/abstractive/summarize-url/', options);
    const results = await response.json();
    const summarize = results.summarize;
    console.log(summarize);
    return summarize;
}


//article extract API   
async function arcticleExtraction(query, numResults, timePeriod, region) {
    const headers = new Headers({
        Origin: "https://chat.openai.com",
        "X-RapidAPI-Key": "YOUR_KEY",
        "X-RapidAPI-Host": "lexper.p.rapidapi.com"
    });
    const searchParams = new URLSearchParams();
    searchParams.set('url', query);
    searchParams.set('js_timeout', '30');
    searchParams.set('media', 'false')
    const url = `https://lexper.p.rapidapi.com/v1.1/extract?${searchParams.toString()}`;
    const response = await fetch(url, { method: "GET", headers, });
    const results = await response.json();
    let text = results.article.text;
    const sentences = text.split(/[,.?!。，？！]/);
    while (sentences.length > 0 && text.length > 2000) {
        const indexToDelete = Math.floor(Math.random() * sentences.length);
        sentences.splice(indexToDelete, 1);
        text = sentences.join('.');
    }
    return text;
}

//Wolfram alpha API
async function WolframAlpha(query, numResults, timePeriod, region) {
    const response = await fetch(
        // YOUR LOCAL SEVER
        `http://localhost:1111?query=${query}`, {
        method: 'GET', mode: 'no-cors'
    });
    const results = response.json();
    console.log(results);
    return results;
}
