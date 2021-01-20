// @flow
import * as React from 'react'

import { Flex } from '@opentrons/components'
import { CommandList } from './CommandList'
import { ClickableDeckMap } from './ClickableDeckMap'

import { getAllDefinitions } from '../labware-defs/utils'

const labwareDefs = getAllDefinitions()

export function HackApp(): React.Node {
  const commands = []
  const labware = [
    {
      labwareId: 'labware-id',
      definition: labwareDefs['opentrons/nest_96_wellplate_200ul_flat/1'],
      location: { slot: 5 },
    },
  ]

  return (
    <Flex flexDirection="row">
      <CommandList commands={commands} />
      <ClickableDeckMap labware={labware} onWellClick={console.log} />
    </Flex>
  )
}
