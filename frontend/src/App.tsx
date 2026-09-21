import { Route, Routes } from 'react-router-dom';
import { AppLayout } from './layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { ActivitiesPage } from './pages/ActivitiesPage';
import { ActivityDetailPage } from './pages/ActivityDetailPage';
import { JournalPage } from './pages/JournalPage';
import { PlanPage } from './pages/PlanPage';

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="activities" element={<ActivitiesPage />} />
        <Route path="activities/:id" element={<ActivityDetailPage />} />
        <Route path="journal" element={<JournalPage />} />
        <Route path="plan" element={<PlanPage />} />
      </Route>
    </Routes>
  );
}

export default App;
