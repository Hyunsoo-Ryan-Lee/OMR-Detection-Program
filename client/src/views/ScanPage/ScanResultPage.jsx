import { useTools } from "libs/utils";

import {
  selectScanType,
  selectScanTypeDetail,
  selectErrorList,
} from "redux/Scan";

import { S3Bucket } from "libs/utils";

import Button from "components/Button";

const ScanResultPage = () => {
  const {
    useEffect,
    useRef,
    useState,
    useNavigate,
    useParams,
    useSelector,
    api,
  } = useTools;
  const navigate = useNavigate();
  const { result_id: resultId } = useParams();

  const [frontImage, setFrontImage] = useState("");
  const [backImage, setBackImage] = useState("");
  const [s3Image, setS3Image] = useState("");
  const [imgType, setImgType] = useState("front");
  const [imgSize, setImgSize] = useState({ width: 0, height: 0 });

  const [inputValue, setInputValue] = useState([]);
  const [errorData, setErrorData] = useState([]);
  const [personalInfo, setPersonalInfo] = useState([]);
  const [personalInfoValue, setPersonalInfoValue] = useState([]);
  const [focusIndex, setFocusIndex] = useState(0);

  const scanType = useSelector(selectScanType);
  const scanTypeDetail = useSelector(selectScanTypeDetail);
  const errorList = useSelector(selectErrorList);

  const errorIdx = errorList.indexOf(resultId);

  const chkMetaTypeArr = ["유아", "초등", "중등", "고등"];
  const chkTypeArr = [
    "개인번호",
    "학년/반/번호",
    "학생 학년/반/번호",
    "자녀의 학년/반/번호",
    "임시배정번호",
  ];

  const extractImagePath = imgPath => {
    return imgPath.split("/").slice(3).join("/");
  };

  const encodeImage = byteData => {
    return "data:image/jpeg;base64," + encode(byteData);
  };

  const onClickImgType = atype => {
    if (atype === "front") {
      setS3Image(frontImage);
      setFocusIndex(0);
      setImgType("front");
    } else {
      setS3Image(backImage);
      setImgType("back");

      const inputArr = document.querySelectorAll(".inputValue");
      if (!inputArr.length) {
        return;
      }
      let chk = false;
      errorData.some((e, idx) => {
        const { boxInfo, section } = e;
        if (section === "back") {
          setFocusIndex(personalInfoValue.length + idx);
          inputArr[personalInfoValue.length + idx].focus();
          inputArr[personalInfoValue.length + idx].select();
          onClickRInfo(boxInfo, section);
          chk = true;
          return true;
        }
      });
      if (!chk) {
        onClickRInfo([0, 0, 0, 0], "back");
      }
    }
  };

  const onClickPrevPage = () => {
    if (errorIdx === 0) {
      alert("처음 페이지입니다");
    } else {
      setFocusIndex(0);
      setImgType("front");
      const nxtTarget = errorList[errorIdx - 1];
      navigate(`/scan/result/${nxtTarget}`);
    }
  };

  const onClickNextPage = () => {
    if (errorIdx === errorList.length - 1) {
      alert("마지막 페이지입니다");
    } else {
      setFocusIndex(0);
      setImgType("front");
      setPersonalInfo([]);
      const nxtTarget = errorList[errorIdx + 1];
      navigate(`/scan/result/${nxtTarget}`);
    }
  };

  const onClickSave = dir => {
    let corrData = [];
    let valid = true;

    for (let i = 0; i < personalInfoValue.length; i++) {
      let corrVal = personalInfoValue[i];
      const { totalOrder } = personalInfo[i];

      if (typeof corrVal === "string") {
        if (corrVal.includes("*")) {
          alert("개인번호 확인해 주세요.");
          valid = false;
          return;
        }
        corrVal = [corrVal];
      }

      let chk = false;
      corrData.forEach(element => {
        if (element.totalOrder === totalOrder) {
          let concatAns = element.answer[0] + corrVal;
          if (concatAns.includes("*")) {
            alert("개인번호 확인해 주세요.");
            valid = false;
            return;
          }
          element.answer = [concatAns];
          chk = true;
        }
      });

      if (!valid) {
        return;
      }

      if (!chk) {
        let obj = { answer: corrVal, totalOrder };
        corrData.push(obj);
      }
    }

    if (!valid) {
      return;
    }

    for (let i = 0; i < inputValue.length; i++) {
      let obj = {};

      let corrVal = inputValue[i];
      if (typeof corrVal === "string") {
        // corrVal = corrVal === " " ? [corrVal] : corrVal.split(" ");
        corrVal = [corrVal];
      }
      obj.answer = corrVal;
      const { totalOrder } = errorData[i];
      obj.totalOrder = totalOrder;
      corrData.push(obj);
    }

    api
      .put(`/api/result/v2/${resultId}`, corrData)
      .then(res => res.data)
      .then(res => {
        const { status } = res;
        if (status) {
          dir === "before" ? onClickPrevPage() : onClickNextPage();
        }
      });
  };

  const onKeyPressHandler = e => {
    const keyType = e.key;
    const currentElem = document.activeElement;
    const inputArr = document.querySelectorAll(".inputValue");

    if (keyType === "PageUp") {
      onClickSave("before");
    } else if (keyType === "PageDown") {
      onClickSave("next");
    } else if (keyType === "F9") {
      onClickSave("next");
    } else if (
      keyType === "Enter" &&
      currentElem.tagName.toLowerCase() === "input"
    ) {
      if (focusIndex < personalInfo.length - 1) {
        let focusIdx = -1;
        for (let i = focusIndex + 1; i < personalInfo.length; i++) {
          const { boxInfo } = personalInfo[i];
          if (JSON.stringify(boxInfo) !== JSON.stringify([0, 0, 0, 0])) {
            focusIdx = i;
            break;
          }
        }
        if (focusIdx !== -1) {
          setTimeout(() => {
            inputArr[focusIdx].focus();
            inputArr[focusIdx].select();
          }, 0.5);
          setFocusIndex(focusIdx);
        } else if (errorData.length) {
          setTimeout(() => {
            inputArr[personalInfo.length].focus();
            inputArr[personalInfo.length].select();
          }, 0.5);
          setFocusIndex(personalInfo.length);
        } else if (focusIdx === -1) {
          onClickSave("next");
        }
      } else if (focusIndex < inputArr.length - 1) {
        setTimeout(() => {
          inputArr[focusIndex + 1].focus();
          inputArr[focusIndex + 1].select();
        }, 0.5);
        setFocusIndex(focusIndex + 1);
      } else {
        onClickSave("next");
      }
    } else if (keyType === "ArrowUp") {
      if (currentElem.tagName.toLowerCase() === "input" && focusIndex > 0) {
        setTimeout(() => {
          inputArr[focusIndex - 1].focus();
          inputArr[focusIndex - 1].select();
        }, 0.5);
        setFocusIndex(focusIndex - 1);
      }
    } else if (keyType === "ArrowDown") {
      if (
        currentElem.tagName.toLowerCase() === "input" &&
        focusIndex < inputArr.length - 1
      ) {
        setTimeout(() => {
          inputArr[focusIndex + 1].focus();
          inputArr[focusIndex + 1].select();
        }, 0.5);
        setFocusIndex(focusIndex + 1);
      }
    }
  };

  const canvas = useRef();
  let ctx = null;

  const loadImageCallback = (func = null) => {
    const canvasElem = canvas.current;
    const { clientWidth, clientHeight } = canvasElem;

    canvasElem.width = clientWidth;
    canvasElem.height = clientHeight;

    if (imgSize.width === 0) {
      setImgSize({ width: clientWidth, height: clientHeight });
    }

    ctx = canvasElem.getContext("2d");

    const image = new Image();
    image.onload = function (_) {
      ctx.drawImage(image, 0, 0, canvasElem.width, canvasElem.height);
      if (func !== null) {
        func();
      }
    };
    image.onerror = _ => {};
    image.src = s3Image;
  };

  const getImage = async params => {
    const data = await S3Bucket.getObject(params).promise();
    return data;
  };
  function encode(data) {
    var str = data.reduce((a, b) => {
      return a + String.fromCharCode(b);
    }, "");
    return btoa(str).replace(/.{76}(?=.)/g, "$&\n");
  }

  const onClickRInfo = (element, section) => {
    const _drawRect = () => {
      element.length >= 1 && element[0].length
        ? element.forEach(e => drawRect(e))
        : drawRect(element);
    };

    if (section === "front") {
      setS3Image(frontImage);
    } else if (backImage) {
      setS3Image(backImage);
    }
    setImgType(section);
    loadImageCallback(_drawRect);
  };

  // draw rectangle
  const drawRect = (info, style = {}) => {
    let [x, y, w, h] = info;
    x *= imgSize.width;
    w *= imgSize.width;
    y *= imgSize.height;
    h *= imgSize.height;

    const { borderColor = "red", borderWidth = 1 } = style;

    ctx.beginPath();
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = borderWidth;
    ctx.rect(x, y, w, h);
    ctx.stroke();
  };

  const updateErrorData = (errorList, valueData) => {
    let tmpErrorData = [];

    let tmpPersonalInfoSet = new Set();

    for (const [, arr] of Object.entries(valueData)) {
      const { totalOrder, questionNumber } = arr;
      if (questionNumber) {
        break;
      }
      tmpPersonalInfoSet.add(totalOrder);
    }

    let tmpInputValue = [];

    errorList.forEach(error => {
      const { errType, boxInfo, totalOrder, section } = error;

      if (!tmpPersonalInfoSet.has(totalOrder)) {
        const origin = valueData[totalOrder];
        tmpErrorData.push({
          errType,
          boxInfo,
          no: origin.questionNumber
            ? `${origin.type} ${origin.questionNumber}`
            : origin.type,
          totalOrder,
          section,
        });
        const originAnswer = origin.answer.join(" ");
        tmpInputValue.push(originAnswer ? originAnswer : " ");
      }
    });
    return [tmpErrorData, tmpInputValue];
  };

  useEffect(() => {
    api
      .get(`/api/result/v2/${resultId}`)
      .then(res => res.data)
      .then(res => {
        const { s3PathDetail, valueList, errorList, metaType } = res.data;

        let valueData = {};
        valueList.forEach(element => {
          valueData[element.totalOrder] = element;
        });

        // 개인정보 입력 및 수정 데이터 관리 ==========
        let tmpPersonalInfo = [];
        let tmpPersonalInfoValue = [];
        let minFocusIdx = -1;
        const chkErrExist = trg => {
          return trg.includes(" ") || trg.includes("*");
        };
        for (const [, arr] of Object.entries(valueData)) {
          const { type, totalOrder, answer, questionNumber } = arr;
          if (questionNumber) {
            break;
          }
          let answerValue = answer ? answer.join(" ") : "";
          let section = "front"; // 개인정보는 무조건 앞면에만 있음
          let chkFocused = false;

          errorList.forEach(e => {
            if (e.totalOrder === totalOrder && minFocusIdx === -1)
              chkFocused = true;
          });

          if (chkMetaTypeArr.includes(metaType) && chkTypeArr.includes(type)) {
            let boxInfo = [0, 0, 0, 0];

            errorList.forEach(e => {
              if (e.totalOrder === totalOrder) {
                boxInfo = e.boxInfo;
              }
            });
            let grade = answerValue[0];
            let cls = answerValue.slice(1, 3);
            let clsNum = answerValue.slice(3, 5);

            tmpPersonalInfoValue.push(grade);
            tmpPersonalInfoValue.push(cls);
            tmpPersonalInfoValue.push(clsNum);

            tmpPersonalInfo.push({
              type: "학년",
              totalOrder,
              answer: grade,
              boxInfo,
              section,
            });

            if (chkFocused && chkErrExist(grade)) {
              setFocusIndex(tmpPersonalInfo.length - 1);
              minFocusIdx = tmpPersonalInfo.length - 1;
            }

            tmpPersonalInfo.push({
              type: "반",
              totalOrder,
              answer: cls,
              boxInfo,
              section,
            });
            if (chkFocused && chkErrExist(cls) && minFocusIdx === -1) {
              setFocusIndex(tmpPersonalInfo.length - 1);
              minFocusIdx = tmpPersonalInfo.length - 1;
            }
            tmpPersonalInfo.push({
              type: "번호",
              totalOrder,
              answer: clsNum,
              boxInfo,
              section,
            });

            if (chkFocused && chkErrExist(clsNum) && minFocusIdx === -1) {
              setFocusIndex(tmpPersonalInfo.length - 1);
              minFocusIdx = tmpPersonalInfo.length - 1;
            }
          } else {
            let boxInfo = [0, 0, 0, 0];
            errorList.forEach(e => {
              if (e.totalOrder === totalOrder) {
                boxInfo = e.boxInfo;
              }
            });
            tmpPersonalInfoValue.push(answerValue);
            tmpPersonalInfo.push({
              type,
              totalOrder,
              answer: answerValue ? answerValue : " ",
              boxInfo,
              section,
            });
            if (chkFocused && chkErrExist(answerValue)) {
              setFocusIndex(tmpPersonalInfo.length - 1);
              minFocusIdx = tmpPersonalInfo.length - 1;
            }
          }
        }
        // ========== 개인정보 입력 및 수정 데이터 관리

        const [tmpErrorData, tmpInputValue] = updateErrorData(
          errorList,
          valueData
        );
        setErrorData(tmpErrorData);
        setInputValue(tmpInputValue);

        setPersonalInfoValue(tmpPersonalInfoValue);
        setPersonalInfo(tmpPersonalInfo);

        const { front: frontImg, back: backImg } = s3PathDetail;
        if (backImg) {
          let backImagePath = extractImagePath(backImg);
          setBackImage(backImagePath);
          getImage({ Key: backImagePath }).then(res => {
            const encodedImage = encodeImage(res.Body);
            setBackImage(encodedImage);
          });
        }

        let frontImagePath = extractImagePath(frontImg);
        getImage({ Key: frontImagePath }).then(res => {
          const encodedImage = encodeImage(res.Body);
          setFrontImage(encodedImage);
          setS3Image(encodedImage);
        });
      });
  }, [resultId]);

  useEffect(() => {
    loadImageCallback();
    const inputArr = document.querySelectorAll(".inputValue");
    if (!inputArr.length) {
      return;
    }

    if (focusIndex === 0 && !personalInfoValue[0].includes(" ")) {
      // 개인정보에 오류가 없는 경우
      const focusIdx =
        personalInfoValue.length < inputArr.length
          ? personalInfoValue.length
          : 0;
      setFocusIndex(focusIdx);
      if (focusIdx >= personalInfo.length && errorData.length) {
        const { boxInfo, section } = errorData[focusIdx - personalInfo.length];
        onClickRInfo(boxInfo, section);
      }
      inputArr[focusIdx].focus();
      inputArr[focusIdx].select();
    } else {
      if (focusIndex >= inputArr.length) {
        return;
      }

      if (imgType === "back") {
        if (focusIndex >= personalInfo.length) {
          const { boxInfo, section } =
            errorData[focusIndex - personalInfo.length];
          if (imgType === section) {
            onClickRInfo(boxInfo, imgType);
            return;
          }
        }
        if (focusIndex < personalInfo.length) {
          // 뒷면 이동 시
          errorData.some((e, idx) => {
            const { boxInfo, section } = e;
            if (section === "back") {
              setFocusIndex(personalInfoValue.length + idx);
              inputArr[personalInfoValue.length + idx].focus();
              inputArr[personalInfoValue.length + idx].select();
              onClickRInfo(boxInfo, section);
              return true;
            }
          });
        }
        onClickRInfo([0, 0, 0, 0], imgType);
        return;
      }

      inputArr[focusIndex].focus();
      inputArr[focusIndex].select();
      if (personalInfo.length && focusIndex < personalInfo.length) {
        const { boxInfo, section } = personalInfo[focusIndex];

        onClickRInfo(boxInfo, section);
      } else if (focusIndex >= personalInfo.length) {
        const { boxInfo, section } =
          errorData[focusIndex - personalInfo.length];
        onClickRInfo(boxInfo, section);
      }
    }
  }, [canvas, s3Image]);

  useEffect(() => {
    // 앞면, 뒷면 버튼 클릭  또는 수정 입력 칸에서 focus 이동 시
    const inputArr = document.querySelectorAll(".inputValue");
    if (!inputArr.length || !personalInfo.length) {
      return;
    }

    if (imgType === "front") {
      if (focusIndex === 0) {
        let focusIdx = -1;
        personalInfo.some((element, idx) => {
          const { boxInfo } = element;
          if (JSON.stringify(boxInfo) !== JSON.stringify([0, 0, 0, 0])) {
            focusIdx = idx;
            return true;
          }
        });
        if (focusIdx === -1) {
          focusIdx = 0;
        }
        setFocusIndex(focusIdx);
        const { boxInfo, section } = personalInfo[focusIdx];
        onClickRInfo(boxInfo, section);
        inputArr[focusIdx].focus();
        inputArr[focusIdx].select();
      }
    } else if (focusIndex < personalInfo.length) {
      // 뒷면 이동 시
      let chk = false;
      errorData.some((e, idx) => {
        const { boxInfo, section } = e;
        if (section === "back") {
          setFocusIndex(personalInfoValue.length + idx);
          inputArr[personalInfoValue.length + idx].focus();
          inputArr[personalInfoValue.length + idx].select();
          onClickRInfo(boxInfo, section);
          chk = true;
          return true;
        }
      });
      if (!chk) {
        if (imgType === "back") {
          return;
        }
        setFocusIndex(personalInfoValue.length);
        onClickRInfo([0, 0, 0, 0], "back");
      }
    }
  }, [imgType]);

  return (
    <div className="mt-6 mx-6" onKeyDown={onKeyPressHandler} tabIndex="0">
      <div className="flex flex-row items-end gap-4 m-3">
        <div className="w-32">
          <div className="border border-teal-400 bg-teal-400 text-white rounded-md p-1">
            <p className="pl-1">{scanType.label ? scanType.label : "없음"}</p>
          </div>
        </div>
        <div className="w-96">
          <div className="border border-teal-400 bg-teal-400 text-white rounded-md p-1">
            <p className="pl-1">
              {scanTypeDetail.label ? scanTypeDetail.label : "없음"}
            </p>
          </div>
        </div>
      </div>
      <div className="mx-2 flex flex-row w-48">
        <Button
          text="앞면"
          main={imgType === "front" ? true : false}
          onClick={() => {
            onClickImgType("front");
          }}
        />
        {backImage ? (
          <Button
            text="뒷면"
            main={imgType === "back" ? true : false}
            onClick={() => {
              onClickImgType("back");
            }}
          />
        ) : (
          <></>
        )}
      </div>

      <div className="grid grid-cols-12 gap-4 m-2 p-1 items-start">
        <div className="col-span-9 w-full overflow-x-auto border-2">
          <canvas className="object-none w-full h-full" ref={canvas} />
        </div>
        <div className="col-span-3 w-full">
          <div className="mb-4 p-1 text-center border border-teal-400 rounded-md  bg-teal-400">
            수정 (현재: {errorIdx + 1} / 전체: {errorList.length})
          </div>
          <div className="flex relative max-h-[500px] flex-auto overflow-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="border border-slate-300 bg-slate-200">No.</th>
                  <th className="border border-slate-300 bg-slate-200">
                    필드명
                  </th>
                  <th className="border border-slate-300 bg-slate-200">답안</th>
                </tr>
              </thead>
              <tbody className="w-full">
                {personalInfo.map((element, idx) => {
                  const { type, boxInfo } = element;
                  const maxLength =
                    type === "학년"
                      ? 1
                      : type === "반" || type === "번호"
                      ? 2
                      : 50;
                  return (
                    <tr
                      className="bg-gray-100"
                      key={idx}
                      onClick={() => {
                        onClickRInfo(boxInfo, "front");
                        setFocusIndex(idx);
                      }}
                      onFocus={() => {
                        onClickRInfo(boxInfo, "front");
                        setFocusIndex(idx);
                      }}
                    >
                      <td className="border border-y-1 border-slate-30 text-center">
                        {idx + 1}
                      </td>
                      <td className="border border-y-1 border-slate-300">
                        <div className="w-20 p-1">{type}</div>
                      </td>
                      <td className="border border-y-1 border-slate-300 text-center">
                        <input
                          className="w-16 h-4 inputValue"
                          value={
                            typeof personalInfoValue[idx] === "string"
                              ? personalInfoValue[idx]
                              : personalInfoValue[idx].join(" ")
                          }
                          onChange={e => {
                            let tmpValue = JSON.parse(
                              JSON.stringify(personalInfoValue)
                            );
                            tmpValue[idx] = e.target.value;
                            setPersonalInfoValue(tmpValue);
                          }}
                          maxLength={maxLength}
                        />
                      </td>
                    </tr>
                  );
                })}
                {errorData.map((element, idx) => {
                  const { errType, no, boxInfo, section } = element;
                  return (
                    <tr
                      className="hover:bg-slate-100 hover:cursor-pointer"
                      onClick={() => {
                        onClickRInfo(boxInfo, section);
                        setFocusIndex(personalInfo.length + idx);
                      }}
                      onFocus={() => {
                        onClickRInfo(boxInfo, section);
                        setFocusIndex(personalInfo.length + idx);
                      }}
                      key={idx}
                    >
                      <td className="border border-y-1 border-slate-30 text-center text-sm">
                        {no}
                      </td>
                      <td className="border border-y-1 border-slate-300">
                        <div className="w-20 p-1">{errType}</div>
                      </td>
                      <td className="border border-y-1 border-slate-300 text-center">
                        <input
                          className="w-16 h-4 inputValue"
                          value={
                            typeof inputValue[idx] === "string"
                              ? inputValue[idx]
                              : inputValue[idx].join(" ")
                          }
                          onChange={e => {
                            let tmpValue = JSON.parse(
                              JSON.stringify(inputValue)
                            );
                            tmpValue[idx] = e.target.value;
                            setInputValue(tmpValue);
                          }}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="pt-16">
            <div className="flex flex-row">
              <Button text="확인/저장(F9)" main={true} onClick={onClickSave} />
              <Button
                text="목록"
                onClick={() => {
                  navigate("/scan");
                }}
              />
            </div>
            <div className="flex flex-row pt-2">
              <Button
                text="이전(PageUp)"
                main={true}
                onClick={() => {
                  onClickSave("before");
                }}
              />
              <Button
                text="다음(PageDown)"
                onClick={() => {
                  onClickSave("next");
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanResultPage;
