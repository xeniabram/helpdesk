import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import { TicketDetailPage } from "./pages/TicketDetailPage";
import { TicketListPage } from "./pages/TicketListPage";

function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <Routes>
          <Route path="/" element={<TicketListPage />} />
          <Route path="/tickets/:id" element={<TicketDetailPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
