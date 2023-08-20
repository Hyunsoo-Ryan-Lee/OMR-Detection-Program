import { createSlice } from "@reduxjs/toolkit";

export const scanSlice = createSlice({
  name: "scan",
  initialState: {
    scanType: {},
    scanTypeDetail: {},
    answerData: [],
    errorList: [],
    errorIdx: 0,
    answerId: "",
    s3PathTree: [],
    method: "normal",
  },
  reducers: {
    setScanType: (state, action) => {
      state.scanType = action.payload;
    },
    setScanTypeDetail: (state, action) => {
      state.scanTypeDetail = action.payload;
    },
    resetScanType: (state, _) => {
      state.scanType = {};
      state.scanTypeDetail = {};
      state.answerData = [];
      state.errorList = [];
      state.errorIdx = 0;
      state.answerId = "";
      state.method = "normal";
    },
    setAnswerData: (state, action) => {
      const data = action.payload;
      state.answerData = data;
    },
    setResultData: (state, action) => {
      const [resultId, data] = action.payload;
      state.answerData[resultId] = data;
    },
    setErrorList: (state, action) => {
      const data = action.payload;
      state.errorList = data;
    },
    setErrorIdx: (state, action) => {
      state.errorIdx = action.payload;
    },
    setAnswerId: (state, action) => {
      state.answerId = action.payload;
    },
    setS3PathTree: (state, action) => {
      state.s3PathTree = action.payload;
    },
    setMethod: (state, action) => {
      state.method = action.payload;
    },
  },
});

export const {
  setScanType,
  setScanTypeDetail,
  resetScanType,
  setAnswerData,
  setResultData,
  setErrorList,
  setErrorIdx,
  setAnswerId,
  setS3PathTree,
  setMethod,
} = scanSlice.actions;

export const selectScanType = state => state.scan.scanType;
export const selectScanTypeDetail = state => state.scan.scanTypeDetail;
export const selectAnswerData = state => state.scan.answerData;

export const selectErrorList = state => state.scan.errorList;
export const selectErrorIdx = state => state.scan.errorIdx;
export const selectCurErrorData = errorIdx => state =>
  state.scan.errorData[errorIdx];
export const selectAnswerId = state => state.scan.answerId;
export const selectS3PathTree = state => state.scan.s3PathTree;
export const selectMethod = state => state.scan.method;

export default scanSlice.reducer;
