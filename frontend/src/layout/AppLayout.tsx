import { NavLink, Outlet } from 'react-router-dom';
import { SportSelector } from '../components/SportSelector';
import { useSportFilter } from '../context/SportFilterContext';
import './AppLayout.css';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/activities', label: 'Activités' },
  { to: '/journal', label: 'Journal' },
  { to: '/plan', label: 'Plan' },
];

export function AppLayout() {
  const { sport, setSport } = useSportFilter();

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-brand">Training Partner</div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `app-nav-link${isActive ? ' active' : ''}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="app-main">
        <header className="app-topbar">
          <SportSelector value={sport} onChange={setSport} />
        </header>
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
