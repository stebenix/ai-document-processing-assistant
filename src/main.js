import './styles.css';
import './mobile-fix.css';
import appHtml from './app.html?raw';
import { loadDashboardData } from './dashboardData.js';

const root = document.getElementById('root');
root.innerHTML = appHtml;

function initPaperloopApp() {

    const pageLinks = document.querySelectorAll('[data-page]');
    const panels = document.querySelectorAll('.page-panel');
    const queueLinks = document.querySelectorAll('[data-utility]');
    const actionLinks = document.querySelectorAll('[data-open-page]');
    const drawer = document.getElementById('drawer');
    const drawerOverlay = document.getElementById('drawerOverlay');
    const menuBtn = document.getElementById('menuBtn');
    const drawerClose = document.getElementById('drawerClose');
    const utilitySheet = document.getElementById('utilitySheet');
    const utilityOverlay = document.getElementById('utilityOverlay');
    const utilityPanels = document.querySelectorAll('.utility-panel');
    const utilityCloseButtons = document.querySelectorAll('#utilityClose, [data-utility-close]');
    function syncBodyLock(){
      const drawerOpen = drawer.classList.contains('open');
      const utilityOpen = utilitySheet.classList.contains('open');
      document.body.style.overflow = (drawerOpen || utilityOpen) ? 'hidden' : '';
    }

    function openDrawer(){
      drawer.classList.add('open');
      drawerOverlay.classList.add('open');
      syncBodyLock();
    }

    function closeDrawer(){
      drawer.classList.remove('open');
      drawerOverlay.classList.remove('open');
      syncBodyLock();
    }

    function openUtility(name){
      utilityPanels.forEach(panel => panel.classList.toggle('active', panel.id === `utility-${name}`));
      utilitySheet.classList.add('open');
      utilityOverlay.classList.add('open');
      utilitySheet.setAttribute('aria-hidden', 'false');
      syncBodyLock();
    }

    function closeUtility(){
      utilitySheet.classList.remove('open');
      utilityOverlay.classList.remove('open');
      utilitySheet.setAttribute('aria-hidden', 'true');
      syncBodyLock();
    }


    function setActivePage(page){
      pageLinks.forEach(link => {
        if(link.dataset.page){
          link.classList.toggle('active', link.dataset.page === page);
        }
      });
      panels.forEach(panel => panel.classList.toggle('active', panel.id === `page-${page}`));
      closeUtility();
      closeDrawer();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    pageLinks.forEach(link => {
      if(link.dataset.page){
        link.addEventListener('click', (e) => {
          e.preventDefault();
          setActivePage(link.dataset.page);
        });
      }
    });

    queueLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        closeDrawer();
        openUtility(link.dataset.utility);
      });
    });

    actionLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        setActivePage(link.dataset.openPage);
      });
    });


    menuBtn.addEventListener('click', openDrawer);
    drawerClose.addEventListener('click', closeDrawer);
    drawerOverlay.addEventListener('click', closeDrawer);
    utilityOverlay.addEventListener('click', closeUtility);
    utilityCloseButtons.forEach(btn => btn.addEventListener('click', closeUtility));

    document.addEventListener('keydown', (e) => {
      if(e.key === 'Escape'){
        closeUtility();
        closeDrawer();
      }
    });
  
}

initPaperloopApp();
loadDashboardData();
