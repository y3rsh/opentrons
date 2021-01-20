// @flow
import * as React from 'react'

import { RobotWorkSpace, LabwareRender } from '@opentrons/components'
import { getDeckDefinitions } from '@opentrons/components/src/deck/getDeckDefinitions'

import type { LabwareDefinition2 } from '@opentrons/shared-data'

const deckDef = getDeckDefinitions()['ot2_standard']

export type LabwareLocation = {
  slot: number,
  ...
}

export type LabwareData = {
  labwareId: string,
  definition: LabwareDefinition2,
  location: LabwareLocation,
  ...
}

export type ClickableDeckMapProps = {|
  labware: Array<LabwareData>,
  onWellClick: (labwareId: string, wellName: string) => mixed,
|}

export function ClickableDeckMap(props: ClickableDeckMapProps): React.Node {
  const { labware, onWellClick } = props
  const [currLabware, setCurrLabware] = React.useState<string | null>(null)
  const [currWell, setCurrWell] = React.useState<string | null>(null)

  return (
    <RobotWorkSpace
      deckLayerBlocklist={[
        'fixedBase',
        'doorStops',
        'metalFrame',
        'removalHandle',
        'removableDeckOutline',
        'screwHoles',
        'calibrationMarkings',
      ]}
      deckDef={deckDef}
      viewBox={`-46 -10 ${488} ${390}`} // TODO: put these in variables
    >
      {({ deckSlotsById }) =>
        labware.map(labwareData => {
          const { labwareId, definition, location } = labwareData
          const isCurrLabware = labwareId === currLabware
          const slotId = `${location.slot}`
          const slotDef = deckSlotsById[slotId]
          const slotOrigin = slotDef.position

          return (
            <g
              key={slotId}
              transform={`translate(${slotOrigin[0]}, ${slotOrigin[1]})`}
              onClick={() => {
                if (isCurrLabware && currWell) {
                  onWellClick(labwareId, currWell)
                }
              }}
            >
              <LabwareRender
                definition={definition}
                selectedWells={
                  isCurrLabware && currWell != null
                    ? { [currWell]: null }
                    : null
                }
                onMouseEnterWell={({ wellName }) => {
                  setCurrLabware(labwareId)
                  setCurrWell(wellName)
                }}
                onMouseLeaveWell={({ wellName }) => {
                  if (isCurrLabware) {
                    setCurrWell(wellName === currWell ? null : currWell)
                  }
                }}
              />
            </g>
          )
        })
      }
    </RobotWorkSpace>
  )
}
