console.log('test_module loaded')

import FetchStore from "https://cdn.jsdelivr.net/npm/@zarrita/storage/fetch/+esm";
import * as zarr from "https://cdn.jsdelivr.net/npm/zarrita/+esm";

import { XMLParser } from "https://cdn.jsdelivr.net/npm/fast-xml-parser/+esm";

const url = 'https://storage.googleapis.com/brim-example-files/drosophila_LSBM.brim.zarr'

let store = new FetchStore(url)
let root = await zarr.open.v3(store, { kind: "group" });

function standardize_path(path) {
  if (!path.endsWith('/')) {
    path = path + '/';
  }
  if (path.startsWith('/')) {
    path = path.slice(1);
  }
  return path;
}

async function list_S3keys(store_url, full_path){

    function split_path(url, full_path) {
      url = standardize_path(url).slice(0,-1);
      full_path = standardize_path(full_path);

      let path = [];
      const last_slash = url.lastIndexOf('/');
      path.endpoint = url.slice(0, last_slash+1)
      path.object = url.slice(last_slash+1) + '/' + full_path
      return path;
    }
    const path = split_path(store_url, full_path);

    let queries = "list-type=2&delimiter=/";
    queries += "&prefix="+path.object;

    let url = path.endpoint + "?" + queries;
    url = encodeURI(url);

    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const xmlText = await response.text();

    // Parse XML using fast-xml-parser
    const parser = new XMLParser();
    const xmlObj = parser.parse(xmlText);

    function ExtractKeyFromPrefix (x) {
        let p = x.Prefix;
        if (p.endsWith('/')) {
            p = p.slice(0, -1)
        }
        p = p.split('/').pop()
        return p;
    }
    // Extract CommonPrefixes
    let prefixes = [];
    if (xmlObj.ListBucketResult && xmlObj.ListBucketResult.CommonPrefixes) {
        const cp = xmlObj.ListBucketResult.CommonPrefixes;
        if (Array.isArray(cp)) {
            prefixes = cp.map(ExtractKeyFromPrefix);
        } else if (cp.Prefix) {
            prefixes = [ExtractKeyFromPrefix(cp.Prefix)];
        }
    }
    return prefixes;
  }
let res = await list_S3keys( store.url, 'Brillouin_data/Data_0/Analysis_0')
console.log(res)