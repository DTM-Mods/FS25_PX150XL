-- The showroom is a display, not a free-standing physics simulation.
-- Keep purchased/leased headers fully dynamic.
PX150ShopDisplay = {}

function PX150ShopDisplay.prerequisitesPresent(specializations)
    return true
end

function PX150ShopDisplay.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onPostLoad", PX150ShopDisplay)
end

function PX150ShopDisplay:onPostLoad(savegame)
    if not self:getIsInShowroom() then
        return
    end

    for _, component in ipairs(self.components) do
        if getRigidBodyType(component.node) == RigidBodyType.DYNAMIC then
            setRigidBodyType(component.node, RigidBodyType.KINEMATIC)
        end
    end
end
