// @flow
import * as React from 'react'

import { Btn, RobotCoordsForeignDiv } from '@opentrons/components'

import type { DeckSlot } from '@opentrons/shared-data'

export type AddLabwareButtonProps = {|
  slot: DeckSlot,
  loadLabware: (loadName: string, slot: string) => mixed,
|}

export function AddLabwareButton(props: AddLabwareButtonProps): React.Node {
  const { slot, loadLabware } = props

  return (
    <RobotCoordsForeignDiv
      x={slot.position[0]}
      y={slot.position[1]}
      width={slot.boundingBox.xDimension}
      height={slot.boundingBox.yDimension}
    >
      <Btn
        onClick={() => console.log('hello')}
        width="100%"
        height="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
        color="white"
        backgroundColor="rgba(0,0,0,0.3)"
      >
        Add Labware
      </Btn>
    </RobotCoordsForeignDiv>
  )
}
