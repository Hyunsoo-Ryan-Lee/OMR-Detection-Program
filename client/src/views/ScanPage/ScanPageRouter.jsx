import { Routes, Route } from "react-router-dom";

import ScanMainPage from "views/ScanPage/ScanMainPage";
import ScanResultPage from "views/ScanPage/ScanResultPage";

const ScanPageRouter = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={<ScanMainPage />} />
        <Route path="/result/:result_id" element={<ScanResultPage />} />
      </Routes>
    </>
  );
};

export default ScanPageRouter;
