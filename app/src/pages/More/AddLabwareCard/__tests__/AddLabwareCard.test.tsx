import * as React from 'react'
import { Provider } from 'react-redux'
import { mountWithStore } from '@opentrons/components/__utils__'

import * as CustomLabware from '../../../../redux/custom-labware'
import * as CustomLabwareFixtures from '../../../../redux/custom-labware/__fixtures__'
import { AddLabwareCard } from '..'
import { ManagePath } from '../ManagePath'
import { AddLabware } from '../AddLabware'
import { AddLabwareFailureModal } from '../AddLabwareFailureModal'

import type { WrapperWithStore } from '@opentrons/components/__utils__'
import type { State, Action } from '../../../../redux/types'

jest.mock('../../../../redux/custom-labware/selectors')

const mockGetCustomLabwareDirectory = CustomLabware.getCustomLabwareDirectory as jest.MockedFunction<
  typeof CustomLabware.getCustomLabwareDirectory
>

const mockGetAddLabwareFailure = CustomLabware.getAddLabwareFailure as jest.MockedFunction<
  typeof CustomLabware.getAddLabwareFailure
>

const mockLabwarePath = '/path/to/labware'

describe('AddLabwareCard', () => {
  let mockStore: React.ComponentProps<typeof Provider>['store']
  let render: () => WrapperWithStore<typeof AddLabwareCard, State, Action>

  beforeEach(() => {
    mockGetCustomLabwareDirectory.mockReturnValue(mockLabwarePath)
    mockGetAddLabwareFailure.mockReturnValue({ file: null, errorMessage: null })

    render = () =>
      mountWithStore<typeof AddLabwareCard, State, Action>(<AddLabwareCard />)
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  it('passes labware directory to ManagePath', () => {
    const { wrapper } = render()
    const detail = wrapper.find(ManagePath)

    expect(mockGetCustomLabwareDirectory).toHaveBeenCalledWith({ state: true })
    expect(detail.prop('path')).toEqual(mockLabwarePath)
  })

  it('passes change path function to ManagePath', () => {
    const { wrapper } = render()
    const control = wrapper.find(ManagePath)
    const expectedChangeAction = CustomLabware.changeCustomLabwareDirectory()

    expect(mockStore.dispatch).toHaveBeenCalledTimes(0)
    control.invoke('onChangePath')?.()
    expect(mockStore.dispatch).toHaveBeenCalledWith(expectedChangeAction)
  })

  it('passes open path function to ManagePath', () => {
    const { wrapper } = render()
    const control = wrapper.find(ManagePath)
    const expectedOpenAction = CustomLabware.openCustomLabwareDirectory()

    expect(mockStore.dispatch).toHaveBeenCalledTimes(0)
    control.invoke('onOpenPath')?.()
    expect(mockStore.dispatch).toHaveBeenCalledWith(expectedOpenAction)
  })

  it('passes reset path function to ManagePath', () => {
    const { wrapper } = render()
    const control = wrapper.find(ManagePath)
    const expectedOpenAction = CustomLabware.resetCustomLabwareDirectory()

    expect(mockStore.dispatch).toHaveBeenCalledTimes(0)
    control.invoke('onResetPath')?.()
    expect(mockStore.dispatch).toHaveBeenCalledWith(expectedOpenAction)
  })

  it('passes dispatch function to AddLabware', () => {
    const { wrapper } = render()
    const control = wrapper.find(AddLabware)
    const expectedAction = CustomLabware.addCustomLabware()

    expect(mockStore.dispatch).toHaveBeenCalledTimes(0)
    control.invoke('onAddLabware')?.()
    expect(mockStore.dispatch).toHaveBeenCalledWith(expectedAction)
  })

  it('renders an AddLabwareFailureModal if add labware fails', () => {
    mockGetAddLabwareFailure.mockReturnValue({
      file: CustomLabwareFixtures.mockInvalidLabware,
      errorMessage: 'AH',
    })

    const { wrapper } = render()
    const modal = wrapper.find(AddLabwareFailureModal)

    expect(modal.props()).toEqual({
      file: CustomLabwareFixtures.mockInvalidLabware,
      errorMessage: 'AH',
      directory: mockLabwarePath,
      onCancel: expect.any(Function),
      onOverwrite: expect.any(Function),
    })
  })

  it('AddLabwareFailureModal onCancel and onOverwrite hooked to dispatch', () => {
    const file = CustomLabwareFixtures.mockDuplicateLabware

    mockGetAddLabwareFailure.mockReturnValue({ file, errorMessage: null })

    const { wrapper } = render()
    const modal = wrapper.find(AddLabwareFailureModal)

    modal.invoke('onCancel')?.()
    expect(mockStore.dispatch).toHaveBeenCalledWith(
      CustomLabware.clearAddCustomLabwareFailure()
    )

    modal.invoke('onOverwrite')?.(file)
    expect(mockStore.dispatch).toHaveBeenCalledWith(
      CustomLabware.addCustomLabware(file)
    )
  })
})
