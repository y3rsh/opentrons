// @flow
import * as React from 'react'

import { HttpApiProvider } from './api'
import { MacroProtocolDesigner } from './MacroProtocolDesigner'

export function HackApp(): React.Node {
  return (
    <HttpApiProvider>
      <MacroProtocolDesigner />
    </HttpApiProvider>
  )
}
