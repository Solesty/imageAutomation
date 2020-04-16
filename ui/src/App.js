import React from 'react';
import logo from './logo.svg';
import { MemoryRouter as Router, useHistory, Switch, Route } from 'react-router-dom'
import './App.css';
import Login from './features/Login';
import Gallery from './features/gallery/Gallery';

function App() {
  // let history = useHistory();

  return (
    <div className="">
      <Router>
        <Switch>
          <Route path="/" exact component={Login} />
          <Route path="/gallery" exact component={Gallery} />
        </Switch>
      </Router>
    </div>
  );
}

export default App;
