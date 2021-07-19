import React from 'react'
import { Redirect, Route } from 'react-router-dom'
import cookies from '../cookies'
import { getItem } from '../storage'
function AuthRoute({ path, component, exact = false, redirect }) {
  if (getItem('student') && cookies.get('token')) {
    return <Route path={path} component={component} exact={exact} />
  } else return <Redirect to={redirect} />
}

export default AuthRoute
