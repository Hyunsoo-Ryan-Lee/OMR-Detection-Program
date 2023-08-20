import {
  setScanType,
  setScanTypeDetail,
  resetScanType,
  setAnswerData,
  setErrorList,
  setAnswerId,
  setMethod,
} from "redux/Scan";

import {
  selectScanType,
  selectScanTypeDetail,
  selectAnswerData,
  selectAnswerId,
  selectMethod,
} from "redux/Scan";

import iconv from "iconv-lite";

import { selectUserInfo } from "redux/User";
import { cls, useTools } from "libs/utils";

import Select from "react-select";
import ScanTableComponent from "views/ScanPage/ScanTableComponent";
import SelectPathModal from "views/ScanPage/SelectPathModal";
import Button from "components/Button";
import LoadingIcon from "static/icons/LoadingIcon";

const { REACT_APP_AWS_S3_BUCKET } = process.env;

const ScanMainPage = () => {
  const { useState, useDispatch, useSelector, useEffect, api } = useTools;
  const dispatch = useDispatch();

  const scanType = useSelector(selectScanType);
  const scanTypeDetail = useSelector(selectScanTypeDetail);
  const userInfo = useSelector(selectUserInfo);
  const answerDataTable = useSelector(selectAnswerData);
  const selectedAnswerId = useSelector(selectAnswerId);
  const method = useSelector(selectMethod);

  const [contentType, setContentType] = useState([]);
  const [contentTypeDetail, setContentTypeDetail] = useState({});
  const [showModal, setShowModal] = useState(false);

  const [selectedPath, setSelectedPath] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [savingText, setSavingText] = useState(false);

  const categoryDetailOptions =
    contentTypeDetail[scanType ? scanType.value : "all"];

  const onChangeScanType = e => {
    dispatch(setScanType(e));
    dispatch(setScanTypeDetail({}));
  };

  const onChangeScanTypeDetail = e => {
    dispatch(setScanTypeDetail(e));
  };

  const errorCategoryOptions = [
    { value: "all", label: "전체" },
    { value: "personal_error", label: "인적정보" },
    { value: "multi_error", label: "이중마크" },
    { value: "empty_error", label: "노마크" },
  ];

  const errorCategory = errorCategoryOptions.filter(e => e.value === method)[0];

  let dupliCheck = new Set();
  if (answerDataTable) {
    for (const { resultId } of answerDataTable) {
      dupliCheck.add(resultId);
    }
  }
  let totalCnt = dupliCheck ? dupliCheck.size : 0;

  const onClickErrorCategory = e => {
    let atype;
    if (e === "normal" || e === "all") {
      atype = e;
      dispatch(setMethod(atype));
    } else {
      atype = e.value;
      dispatch(setMethod(atype));
    }
    if (selectedAnswerId) {
      api
        .get(`/api/answer/v2/${selectedAnswerId}?atype=${atype}`)
        .then(res => res.data)
        .then(res => {
          const { result, errors } = res.data;
          dispatch(setAnswerData(result));
          dispatch(setErrorList(errors));
        });
    }
  };

  const submitScan = () => {
    let pathSet = new Set();
    selectedPath.forEach(path => {
      let eachPath = path.split("/");
      eachPath = eachPath.slice(0, -1).join("/");
      pathSet.add(eachPath);
    });
    pathSet = Array.from(pathSet);

    if (pathSet.length >= 2 || pathSet.length === 0) {
      alert("하나의 폴더만 선택해야 합니다.");
    } else {
      const s3Path = `s3://${REACT_APP_AWS_S3_BUCKET}${pathSet[0]}/`;
      setScanning(true);

      const data = {
        objectId: scanTypeDetail.value,
        s3_path: s3Path,
        user_id: userInfo.userId,
      };
      api
        .post("/api/answer", data)
        .then(res => res.data)
        .then(res => {
          const { answer_id: answerId } = res.data;
          dispatch(setAnswerId(answerId));
          api
            .get(`/api/answer/v2/${answerId}?atype=${method}`)
            .then(res => res.data)
            .then(res => {
              const { result, errors } = res.data;
              dispatch(setErrorList(errors));
              dispatch(setAnswerData(result));
              setScanning(false);
              setShowModal(false);
            })
            .catch(err => {
              setScanning(false);
              setShowModal(false);
              let detailMsg = "";
              if (err.config && err.config.data) {
                detailMsg = err.config.data;
              }
              alert(
                `오류가 발생했습니다. 관리자에게 문의해 주세요 \n${detailMsg}`
              );
            });
        })
        .catch(err => {
          setScanning(false);
          setShowModal(false);
          let detailMsg = "";
          if (err.config && err.config.data) {
            detailMsg = err.config.data;
          }
          alert(`오류가 발생했습니다. 관리자에게 문의해 주세요 \n${detailMsg}`);
        });
    }
  };

  const submitSaveTxt = () => {
    api
      .get(`/api/answer/v2/${selectedAnswerId}/save`)
      .then(res => res.data)
      .then(res => {
        const { status } = res;

        if (!status) {
          alert("개인번호 수정이 완료되지 않았습니다. 다시 확인해 주세요");
          return;
        }

        const { txt, fileName } = res.data;

        const element = document.createElement("a");

        let encodedTxt = iconv.encode(txt, "cp-949"); // "windows-1252" or "euc-kr"

        const file = new Blob([encodedTxt], {
          type: "text/plain;charset=cp-949;",
        });
        element.href = URL.createObjectURL(file);
        element.download = `${fileName}.txt`;
        document.body.appendChild(element);
        element.click();
        dispatch(resetScanType());
      })
      .catch(err => {
        let detailMsg = "";
        console.log("err: ", err);
        if (err.config && err.config.data) {
          detailMsg = err.config.data;
        }
        setSavingText(false);
        alert(`오류가 발생했습니다. 관리자에게 문의해 주세요 \n${detailMsg}`);
      });
  };

  useEffect(() => {
    api
      .get("/api/index")
      .then(res => res.data)
      .then(res => {
        const contents = res.data;
        let tmpContentTypeDetail = {};
        contents.forEach(element => {
          const { content_level, content, objectId } = element;
          const processed_data = {
            value: objectId,
            label: content,
          };

          if (content_level in tmpContentTypeDetail) {
            tmpContentTypeDetail[content_level].push(processed_data);
          } else {
            tmpContentTypeDetail[content_level] = [processed_data];
          }
        });

        let tmpContentType = [{ value: "all", label: "전체" }];
        let allDetailOptions = [];

        for (const [k, arr] of Object.entries(tmpContentTypeDetail)) {
          tmpContentType.push({ value: k, label: k });
          arr.forEach(val => {
            allDetailOptions.push(val);
          });
        }
        setContentType(tmpContentType);

        tmpContentTypeDetail.all = allDetailOptions;
        setContentTypeDetail(tmpContentTypeDetail);
      });

    if (selectedAnswerId && method) {
      api
        .get(`/api/answer/v2/${selectedAnswerId}?atype=${method}`)
        .then(res => res.data)
        .then(res => {
          const { result, errors } = res.data;
          dispatch(setErrorList(errors));
          dispatch(setAnswerData(result));
        });
    }
  }, []);

  return (
    <div className="mt-6 mx-12">
      <div className="flex flex-col px-2 gap-6">
        <div className="flex flex-col gap-4 w-2/5">
          <div className="flex flex-row justify-center items-center gap-2">
            <p className="w-1/2">답안지 양식 그룹</p>
            <Select
              className="w-full"
              options={contentType}
              onChange={onChangeScanType}
              value={
                scanType.value
                  ? scanType
                  : { label: "::: 선 택 :::", value: "" }
              }
            />
          </div>
          <div className="flex flex-row justify-center items-center gap-2">
            <p className="w-1/2">답안지 양식 선택</p>
            <Select
              className="w-full"
              options={categoryDetailOptions}
              onChange={onChangeScanTypeDetail}
              value={
                scanTypeDetail.value
                  ? scanTypeDetail
                  : { label: "::: 선 택 :::", value: "" }
              }
            />
          </div>
        </div>
        <div className="flex flex-row -mx-1">
          <Button
            className="w-64"
            text="파일 판독"
            main={true}
            onClick={() => {
              if (scanTypeDetail.value) {
                setShowModal(true);
              } else {
                alert("답안지 양식을 먼저 선택해 주세요.");
              }
            }}
          />
          <Button
            className="w-64"
            text="목록 초기화"
            main={true}
            onClick={() => {
              if (window.confirm("초기화 하시겠습니까?")) {
                dispatch(resetScanType());
                setScanning(false);
              }
            }}
          />
        </div>
        <div className="grid border-b w-1/4 grid-cols-2 gap-2">
          <button
            className={cls(
              "pb-4 font-medium border-b-2",
              method === "normal"
                ? "border-teal-400 text-teal-400"
                : "border-transparent text-gray-500"
            )}
            onClick={() => {
              onClickErrorCategory("normal");
            }}
          >
            스캔
          </button>
          <button
            className={cls(
              "pb-4 font-medium border-b-2",
              method !== "normal"
                ? "border-teal-400 text-teal-400"
                : "border-transparent text-gray-500"
            )}
            onClick={() => {
              onClickErrorCategory("all");
            }}
          >
            검색 수정
          </button>
        </div>
        <div className="flex flex-row items-center">
          {method !== "normal" ? (
            <>
              <div className="flex flex-row items-center justify-center py-2 px-4 border border-transparent rounded-l-md shadow-sm bg-teal-400 text-white text-sm font-medium">
                선택
              </div>
              <Select
                className="w-32"
                options={errorCategoryOptions}
                onChange={onClickErrorCategory}
                value={
                  errorCategory.value
                    ? errorCategory
                    : { label: "::: 선 택 :::", value: "" }
                }
              />
            </>
          ) : (
            <></>
          )}
          <div className="flex flex-row items-center justify-center m-1 py-2 px-20 border border-gray-300 shadow-sm bg-white rounded-md gap-2">
            <div>COUNT:</div>
            <div className="px-1">{answerDataTable.length}</div>
          </div>
          {savingText ? (
            <div className="flex flex-row w-48 items-center justify-center m-1 py-2 px-4 border border-transparent rounded-md shadow-sm bg-teal-400 hover:bg-teal-600 text-white text-sm font-medium focus:ring-2 focus:ring-offset-2 focus:ring-teal-400 focus:outline-none">
              <div>
                <LoadingIcon />
              </div>
              <div>작업 중...</div>
            </div>
          ) : (
            <Button
              className="w-64"
              text="TXT로 저장"
              main={true}
              onClick={() => {
                submitSaveTxt();
              }}
              disabled={totalCnt || savingText ? false : true}
            />
          )}
        </div>
        <div className="max-h-[500px] overflow-auto border rounded-md">
          <ScanTableComponent data={answerDataTable} method={method} />
        </div>
      </div>
      <div className="flex flex-col items-end mt-16"></div>
      {showModal ? (
        <SelectPathModal
          setSelectedPath={setSelectedPath}
          scanning={scanning}
          submitScan={submitScan}
          setShowModal={setShowModal}
          setScanning={setScanning}
        />
      ) : (
        <></>
      )}
    </div>
  );
};
export default ScanMainPage;
