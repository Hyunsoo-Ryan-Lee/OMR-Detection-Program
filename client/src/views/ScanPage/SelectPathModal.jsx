import { useTools } from "libs/utils";

import Button from "components/Button";
import TreeviewComponent from "components/TreeviewComponent";
import LoadingIcon from "static/icons/LoadingIcon";

import { S3Bucket, convertTreeStructure } from "libs/utils";

const SelectPathModal = ({
  setSelectedPath,
  scanning,
  submitScan,
  setShowModal,
  setScanning,
}) => {
  const { useEffect, useState } = useTools;

  const params = { Prefix: "workspace/" };
  const getS3PathList = async (params, ret) => {
    const data = await S3Bucket.listObjectsV2(params).promise();
    data.Contents.forEach(elem => {
      ret.push(elem.Key);
    });
    if (data.IsTruncated) {
      let obj = Object.assign({}, params, {
        ContinuationToken: data.NextContinuationToken,
      });
      return getS3PathList(obj, ret);
    }
    return ret;
  };

  const [s3PathTree, setS3PathTree] = useState([]);
  useEffect(() => {
    getS3PathList(params, []).then(res => {
      const tree = convertTreeStructure(res);
      setS3PathTree(tree);
    });
  }, []);

  return (
    <>
      <div className="justify-center items-center flex fixed inset-0 z-50 outline-none focus:outline-none">
        <div className="relative w-auto my-6 mx-auto max-w-3xl">
          <div className="border-0 rounded-lg shadow-lg relative flex flex-col w-full bg-white outline-none focus:outline-none">
            <div className="flex items-start justify-between p-5 border-b border-solid border-slate-200 rounded-t">
              <h3 className="text-xl font-semibold">판독 경로 선택하기</h3>
            </div>
            <div className="relative p-6 flex-auto">
              <div className="h-[400px] overflow-auto">
                {s3PathTree && s3PathTree.length ? (
                  <TreeviewComponent
                    data={s3PathTree}
                    setSelectedPath={setSelectedPath}
                  />
                ) : (
                  <LoadingIcon />
                )}
              </div>
            </div>
            <div className="flex items-center justify-between p-12 border-t border-solid border-slate-200 rounded-b gap-6">
              {scanning ? (
                <div className="flex flex-row w-48 items-center justify-center m-1 py-2 px-4 border border-transparent rounded-md shadow-sm bg-teal-400 hover:bg-teal-600 text-white text-sm font-medium focus:ring-2 focus:ring-offset-2 focus:ring-teal-400 focus:outline-none">
                  <div>
                    <LoadingIcon />
                  </div>
                  <div>작업 중...</div>
                </div>
              ) : (
                <Button
                  className="w-48"
                  text="작업 시작"
                  main={true}
                  onClick={submitScan}
                />
              )}
              <Button
                className="w-48"
                text="닫기"
                onClick={() => {
                  setShowModal(false);
                  setScanning(false);
                }}
              />
            </div>
          </div>
        </div>
      </div>
      <div className="opacity-25 fixed inset-0 z-40 bg-black"></div>
    </>
  );
};

export default SelectPathModal;
