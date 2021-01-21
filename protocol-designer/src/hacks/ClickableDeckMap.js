// @flow
import * as React from 'react'

import { C_BLUE, RobotWorkSpace, LabwareRender } from '@opentrons/components'
import { getDeckDefinitions } from '@opentrons/components/src/deck/getDeckDefinitions'

import type { LabwareData } from './labware-types'
import type { Highlight } from './ui-types'

const deckDef = getDeckDefinitions()['ot2_standard']

export type ClickableDeckMapProps = {|
  labware: Array<LabwareData>,
  highlights: Array<Highlight>,
  onWellClick: (labwareId: string, wellName: string) => mixed,
|}

export function ClickableDeckMap(props: ClickableDeckMapProps): React.Node {
  const { labware, highlights, onWellClick } = props
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
          const labwareHighlight = highlights.some(
            h => h.labwareId === labwareId && !h.wellName
          )

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
              {labwareHighlight && (
                <rect
                  width={slotDef.boundingBox.xDimension}
                  height={slotDef.boundingBox.yDimension}
                  fill={C_BLUE}
                  rx="4"
                  ry="4"
                />
              )}
              <LabwareRender
                definition={definition}
                selectedWells={
                  isCurrLabware && currWell != null
                    ? { [currWell]: null }
                    : null
                }
                highlightedWells={highlights.reduce((wellMap, highlight) => {
                  if (highlight.labwareId === labwareId && highlight.wellName) {
                    wellMap[highlight.wellName] = null
                  }
                  return wellMap
                }, {})}
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
