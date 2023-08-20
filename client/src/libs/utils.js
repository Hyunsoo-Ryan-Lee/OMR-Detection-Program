import { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

import AWS from "aws-sdk";

const {
  REACT_APP_AWS_ACCESS_KEY_ID,
  REACT_APP_AWS_SECRET_ACCESS_KEY,
  REACT_APP_AWS_S3_BUCKET,
  REACT_APP_AWS_REGION_NAME,
  REACT_APP_BACKEND_IP,
  NODE_ENV,
} = process.env;

const api = axios.create({
  baseURL:
    NODE_ENV === "production"
      ? `http://${REACT_APP_BACKEND_IP}`
      : "http://localhost:8000",
});
api.defaults.timeout = 600000;

export const useTools = {
  useState,
  useEffect,
  useRef,
  useNavigate,
  useParams,
  useSelector,
  useDispatch,
  api,
};

export function cls(...classnames) {
  return classnames.join(" ");
}

AWS.config.update({
  accessKeyId: REACT_APP_AWS_ACCESS_KEY_ID,
  secretAccessKey: REACT_APP_AWS_SECRET_ACCESS_KEY,
});

export const S3Bucket = new AWS.S3({
  params: { Bucket: REACT_APP_AWS_S3_BUCKET },
  region: REACT_APP_AWS_REGION_NAME,
});

export const convertTreeStructure = arr => {
  arr.sort();
  let amap = Object();
  for (const elem of arr) {
    let parentDir = elem.split("/");

    let k = "/" + parentDir.slice(0, -1).join("/");
    let v = parentDir[parentDir.length - 1];

    if (!v) {
      continue;
    }
    if (k in amap) {
      amap[k].push(v);
    } else {
      amap[k] = [v];
    }
  }

  let tree = [];
  for (const elem of arr) {
    let parentDir = elem.split("/");
    let alist = parentDir.slice(0, -1);
    let label = parentDir[parentDir.length - 1];

    if (!label) {
      continue;
    }
    let trg = tree;

    for (let i_f = 0; i_f < alist.length; i_f++) {
      let cur_f = "/" + alist.slice(0, i_f + 1).join("/");
      let chkd = false;
      trg.forEach(t => {
        if (t.value === cur_f) {
          trg = t.children;
          chkd = true;
          return;
        }
      });
      if (chkd) {
        continue;
      }
      let newChildrenValue = [];
      if (cur_f in amap) {
        for (const fileName of amap[cur_f]) {
          newChildrenValue.push({
            value: `${cur_f}/${fileName}`,
            label: fileName,
            showCheckbox: false,
          });
        }
      }
      const newValue = {
        value: cur_f,
        label: alist[i_f],
        children: newChildrenValue,
      };
      trg.push(newValue);
      trg = newValue.children;
    }
  }
  return tree;
};
