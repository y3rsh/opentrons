// @flow
import * as React from 'react'

import { HttpApiProvider } from './api'
import { MacroProtocolDesigner } from './MacroProtocolDesigner'
import { PortalRoot } from '../components/portals/TopPortal'

import '../css/reset.css'

export function HackApp(): React.Node {
  return (
    <HttpApiProvider>
      <MacroProtocolDesigner />
      <PortalRoot />
    </HttpApiProvider>
  )
}
