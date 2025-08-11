import { bw as hasOwn, j as jsxRuntimeExports, bx as Emotion$1, by as createEmotionProps } from "./index-xZiJ-BeD.js";
var Fragment = jsxRuntimeExports.Fragment;
var jsx = function jsx2(type, props, key) {
  if (!hasOwn.call(props, "css")) {
    return jsxRuntimeExports.jsx(type, props, key);
  }
  return jsxRuntimeExports.jsx(Emotion$1, createEmotionProps(type, props), key);
};
var jsxs = function jsxs2(type, props, key) {
  if (!hasOwn.call(props, "css")) {
    return jsxRuntimeExports.jsxs(type, props, key);
  }
  return jsxRuntimeExports.jsxs(Emotion$1, createEmotionProps(type, props), key);
};
export {
  Fragment as F,
  jsxs as a,
  jsx as j
};
