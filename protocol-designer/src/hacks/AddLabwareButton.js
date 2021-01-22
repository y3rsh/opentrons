// @flow
import * as React from 'react'

import {
  useHover,
  useTooltip,
  Icon,
  Box,
  Btn,
  Tooltip,
  RobotCoordsForeignDiv,
} from '@opentrons/components'

import map from 'lodash/map'
import groupBy from 'lodash/groupBy'
import Select from 'react-select'
import { getOnlyLatestDefs } from '../labware-defs'
import { Portal } from '../components/portals/TopPortal'

import type { DeckSlot } from '@opentrons/shared-data'

const LABWARE_OPTIONS_BY_CATEGORY = groupBy(
  getOnlyLatestDefs(),
  'metadata.displayCategory'
)
const LABWARE_OPTIONS = map(
  LABWARE_OPTIONS_BY_CATEGORY,
  (labwareGroup, category) => {
    return {
      label: category,
      options: labwareGroup.map(lw => ({
        label: lw.metadata.displayName,
        value: {
          loadName: lw.parameters.loadName,
          namespace: lw.namespace,
          version: lw.version,
        },
      })),
    }
  }
).filter(g => g.label !== 'trash')

export type AddLabwareButtonProps = {|
  slot: DeckSlot,
  loadLabware: (params: mixed) => mixed,
|}

export function AddLabwareButton(props: AddLabwareButtonProps): React.Node {
  const { slot, loadLabware } = props
  const [showLabwareMenu, setShowLabwareMenu] = React.useState(false)
  const [hovered, hoverHandlers] = useHover({ leaveDelay: 25 })
  const [targetProps, tooltipProps] = useTooltip({ offset: -25 })

  React.useEffect(() => {
    if (!hovered) {
      setShowLabwareMenu(false)
    }
  }, [hovered])

  return (
    <RobotCoordsForeignDiv
      x={slot.position[0]}
      y={slot.position[1]}
      width={slot.boundingBox.xDimension}
      height={slot.boundingBox.yDimension}
      innerDivProps={{
        ...targetProps,
        ...hoverHandlers,
        width: '100%',
        height: '100%',
        position: 'relative',
      }}
    >
      {hovered === true ? (
        <Btn
          onClick={() => setShowLabwareMenu(true)}
          width={slot.boundingBox.xDimension}
          height={slot.boundingBox.yDimension}
          borderRadius="0.5rem"
          display="flex"
          alignItems="center"
          justifyContent="center"
          color="white"
          backgroundColor="rgba(0,0,0,0.5)"
        >
          <Icon width="1em" name="plus" />
          Add Labware
        </Btn>
      ) : null}
      {showLabwareMenu === true ? (
        <Portal>
          <Tooltip visible={showLabwareMenu} {...tooltipProps}>
            <Box color="black" width="16rem" height="19rem">
              <Select
                menuIsOpen
                maxMenuHeight="16rem"
                options={LABWARE_OPTIONS}
                onChange={({ value }) => {
                  loadLabware(value)
                  setShowLabwareMenu(false)
                }}
              />
            </Box>
          </Tooltip>
        </Portal>
      ) : null}
    </RobotCoordsForeignDiv>
  )
}
