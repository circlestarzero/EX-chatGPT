import { result } from "lodash-es"
import { API, getDefaultAPI, getsavedAPIs } from "src/util/apiManager"

export interface SearchResult {
    body: string
    href: string
    title: string
}
type FunctionArgs = { [key: string]: any };
type FunctionType = (...args: any[]) => any;

function stringToFunction(str: string): FunctionType | undefined {
  try {
    const fn = new Function(`return ${str}`)();
    if (typeof fn === 'function') {
      return fn as FunctionType;
    }
  } catch (e) {
    console.error('Error while converting string to function:', e);
  }
  return undefined;
}

function safeStringToFunction<T extends FunctionArgs>(
  str: string,
  argTypes: T
): ((args: T) => ReturnType<FunctionType>) | undefined {
  const fn = stringToFunction(str);
  if (typeof fn === 'function') {
    return ((args: T) => fn(...Object.values(args))) as (
      args: T
    ) => ReturnType<FunctionType>;
  }
  return undefined;
}

export async function apiSearch(query: string, numResults: number, timePeriod: string, region: string, apiUUID: string): Promise<SearchResult[]> {
    const savedAPIS = await getsavedAPIs()
    const api_result = savedAPIS.find((i: API) => i.uuid === apiUUID) || getDefaultAPI()
    const api = api_result.text
    const FunctionString = api;
    const api_function = safeStringToFunction(FunctionString, { query: '', numResults: 0, timePeriod: '',region: '' });
    if (api_function) {
        const q = query,n = numResults, t = timePeriod, r = region;
        const result = api_function({query: q, numResults: n, timePeriod: t, region: r});
        console.log(result); // Output: 3
        return result;
    }
    return JSON.parse('{}');
}

